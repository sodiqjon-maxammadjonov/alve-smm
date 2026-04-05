"""
database.py — Zendor SMM Bot
PostgreSQL (asyncpg) ma'lumotlar bazasi.

Yangi jadval qo'shish uchun:
  1. init_db() funksiyasiga CREATE TABLE yozing
  2. Tegishli CRUD funksiyalarini quyidagi bo'limlarga qo'shing
"""

import asyncpg
import os
import time

_pool: asyncpg.Pool | None = None


# ═══════════════════════════════════════════════════════════════
#  CONNECTION POOL
# ═══════════════════════════════════════════════════════════════

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            os.getenv("DATABASE_URL"),
            ssl="require",
            min_size=2,
            max_size=10,
        )
    return _pool


# ═══════════════════════════════════════════════════════════════
#  INIT — Jadvallarni yaratish
# ═══════════════════════════════════════════════════════════════

async def init_db() -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        # ── users ──────────────────────────────────────────────
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id         BIGINT  PRIMARY KEY,
                username        TEXT    DEFAULT '',
                full_name       TEXT    DEFAULT '',
                balance         BIGINT  DEFAULT 0,
                referred_by     BIGINT  DEFAULT NULL,
                ref_bonus_given INTEGER DEFAULT 0,
                discount        FLOAT   DEFAULT 0,
                created_at      BIGINT  DEFAULT 0
            )
        """)
        # Eski jadvallarga ustun qo'shish (migration)
        for migration in [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS discount FLOAT DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS ref_bonus_given INTEGER DEFAULT 0",
        ]:
            try:
                await conn.execute(migration)
            except Exception:
                pass

        # ── orders ─────────────────────────────────────────────
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id            SERIAL  PRIMARY KEY,
                user_id       BIGINT  NOT NULL,
                smm_order_id  BIGINT,
                service_id    BIGINT,
                service_name  TEXT    DEFAULT '',
                platform      TEXT    DEFAULT '',
                link          TEXT    DEFAULT '',
                quantity      INTEGER DEFAULT 0,
                price_uzs     BIGINT  DEFAULT 0,
                status        TEXT    DEFAULT 'Pending',
                created_at    BIGINT  DEFAULT 0
            )
        """)

        # ── deposits ───────────────────────────────────────────
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id            SERIAL  PRIMARY KEY,
                user_id       BIGINT  NOT NULL,
                amount        BIGINT  DEFAULT 0,
                status        TEXT    DEFAULT 'pending',
                check_file_id TEXT    DEFAULT '',
                reject_reason TEXT    DEFAULT NULL,
                created_at    BIGINT  DEFAULT 0,
                confirmed_at  BIGINT  DEFAULT 0
            )
        """)
        try:
            await conn.execute(
                "ALTER TABLE deposits ADD COLUMN IF NOT EXISTS reject_reason TEXT"
            )
        except Exception:
            pass

        # ── referral_earnings ──────────────────────────────────
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS referral_earnings (
                id          SERIAL  PRIMARY KEY,
                owner_id    BIGINT  NOT NULL,
                from_user   BIGINT  NOT NULL,
                amount      BIGINT  DEFAULT 0,
                order_price BIGINT  DEFAULT 0,
                type        TEXT    DEFAULT '',
                created_at  BIGINT  DEFAULT 0
            )
        """)


# ═══════════════════════════════════════════════════════════════
#  FOYDALANUVCHILAR
# ═══════════════════════════════════════════════════════════════

async def get_or_create_user(
    user_id: int,
    username: str,
    full_name: str,
    referred_by: int | None = None,
) -> bool:
    """Yangi foydalanuvchi bo'lsa True, eski bo'lsa False qaytaradi."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_id FROM users WHERE user_id = $1", user_id
        )
        if row:
            # Username / full_name yangilash
            await conn.execute(
                "UPDATE users SET username=$1, full_name=$2 WHERE user_id=$3",
                username or "", full_name or "", user_id,
            )
            return False
        await conn.execute(
            "INSERT INTO users (user_id, username, full_name, referred_by, created_at) "
            "VALUES ($1, $2, $3, $4, $5)",
            user_id, username or "", full_name or "",
            referred_by, int(time.time()),
        )
        return True


async def get_user(user_id: int) -> dict | None:
    """To'liq user ma'lumotlari."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1", user_id
        )
        return dict(row) if row else None


async def get_balance(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT balance FROM users WHERE user_id = $1", user_id
        )
        return int(row["balance"]) if row else 0


async def update_balance(user_id: int, amount: int) -> None:
    """Balansga amount qo'shadi (manfiy bo'lsa kamaytiradi)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = balance + $1 WHERE user_id = $2",
            amount, user_id,
        )


async def deduct_balance(user_id: int, amount: int) -> bool:
    """
    Balansdan amount ayiradi.
    Yetarli bo'lmasa False qaytaradi (tranzaksiya bilan xavfsiz).
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT balance FROM users WHERE user_id = $1 FOR UPDATE", user_id
            )
            if not row or int(row["balance"]) < amount:
                return False
            await conn.execute(
                "UPDATE users SET balance = balance - $1 WHERE user_id = $2",
                amount, user_id,
            )
    return True


async def set_balance(user_id: int, new_balance: int) -> int:
    """Balansni to'g'ridan-to'g'ri o'rnatadi. Eski qiymatni qaytaradi."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT balance FROM users WHERE user_id = $1", user_id
        )
        old = int(row["balance"]) if row else 0
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE user_id = $2", new_balance, user_id
        )
        return old


async def get_user_discount(user_id: int) -> float:
    """Foydalanuvchi chegirmasi (0 = oddiy narx)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT discount FROM users WHERE user_id = $1", user_id
        )
        return float(row["discount"]) if row else 0.0


async def set_user_discount(user_id: int, discount: float) -> bool:
    """Chegirma o'rnatish (-100..100). Foydalanuvchi topilmasa False."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_id FROM users WHERE user_id = $1", user_id
        )
        if not row:
            return False
        await conn.execute(
            "UPDATE users SET discount = $1 WHERE user_id = $2", discount, user_id
        )
        return True


async def get_all_user_ids() -> list[int]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
    return [r["user_id"] for r in rows]


# ═══════════════════════════════════════════════════════════════
#  BUYURTMALAR
# ═══════════════════════════════════════════════════════════════

async def create_order(
    user_id: int,
    smm_order_id: int,
    service_id: int,
    service_name: str,
    platform: str,
    link: str,
    quantity: int,
    price_uzs: int,
) -> int:
    """Yangi buyurtma yaratadi. ID qaytaradi."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO orders
               (user_id, smm_order_id, service_id, service_name,
                platform, link, quantity, price_uzs, created_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
               RETURNING id""",
            user_id, smm_order_id, service_id, service_name,
            platform, link, quantity, price_uzs, int(time.time()),
        )
        return row["id"]


async def get_user_orders(user_id: int, limit: int = 20) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2",
            user_id, limit,
        )
        return [dict(r) for r in rows]


async def update_order_status(smm_order_id: int, status: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE orders SET status = $1 WHERE smm_order_id = $2",
            status, smm_order_id,
        )


async def get_order_by_smm_id(smm_order_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM orders WHERE smm_order_id = $1", smm_order_id
        )
        return dict(row) if row else None


async def get_active_orders(limit: int = 100) -> list[dict]:
    """Auto-updater uchun — faqat aktiv buyurtmalar."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM orders
               WHERE status NOT IN ('Completed','Canceled','Cancelled','Refunded','Partial')
               ORDER BY created_at DESC LIMIT $1""",
            limit,
        )
        return [dict(r) for r in rows]


async def get_all_orders_paginated(
    page: int = 0,
    page_size: int = 5,
    status_filter: str | None = None,
) -> tuple[list[dict], int]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if status_filter:
            rows = await conn.fetch(
                """SELECT o.*, u.full_name, u.username FROM orders o
                   JOIN users u ON o.user_id = u.user_id
                   WHERE o.status = $1
                   ORDER BY o.created_at DESC LIMIT $2 OFFSET $3""",
                status_filter, page_size, page * page_size,
            )
            total_row = await conn.fetchrow(
                "SELECT COUNT(*) AS cnt FROM orders WHERE status = $1", status_filter
            )
        else:
            rows = await conn.fetch(
                """SELECT o.*, u.full_name, u.username FROM orders o
                   JOIN users u ON o.user_id = u.user_id
                   ORDER BY o.created_at DESC LIMIT $1 OFFSET $2""",
                page_size, page * page_size,
            )
            total_row = await conn.fetchrow("SELECT COUNT(*) AS cnt FROM orders")
        return [dict(r) for r in rows], int(total_row["cnt"])


# ═══════════════════════════════════════════════════════════════
#  DEPOZITLAR
# ═══════════════════════════════════════════════════════════════

async def create_deposit(user_id: int, amount: int, check_file_id: str) -> int:
    """Yangi depozit so'rovi. ID qaytaradi."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO deposits (user_id, amount, check_file_id, created_at)
               VALUES ($1,$2,$3,$4) RETURNING id""",
            user_id, amount, check_file_id, int(time.time()),
        )
        return row["id"]


async def get_deposit_status(deposit_id: int) -> str | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT status FROM deposits WHERE id = $1", deposit_id
        )
        return row["status"] if row else None


async def get_pending_deposits() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT d.*, u.full_name FROM deposits d
               JOIN users u ON d.user_id = u.user_id
               WHERE d.status = 'pending'
               ORDER BY d.created_at DESC""",
        )
        return [dict(r) for r in rows]


async def confirm_deposit(deposit_id: int) -> tuple[int, int, int | None] | None:
    """
    Depozitni tasdiqlaydi, balansga qo'shadi.
    Qaytaradi: (user_id, amount, referrer_id) yoki None.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            dep = await conn.fetchrow(
                "SELECT user_id, amount, status FROM deposits WHERE id = $1 FOR UPDATE",
                deposit_id,
            )
            if not dep or dep["status"] == "confirmed":
                return None

            user_id = dep["user_id"]
            amount  = int(dep["amount"])

            await conn.execute(
                "UPDATE deposits SET status='confirmed', confirmed_at=$1 WHERE id=$2",
                int(time.time()), deposit_id,
            )
            await conn.execute(
                "UPDATE users SET balance = balance + $1 WHERE user_id = $2",
                amount, user_id,
            )

            ref_row = await conn.fetchrow(
                "SELECT referred_by FROM users WHERE user_id = $1", user_id
            )
            referrer_id = ref_row["referred_by"] if ref_row else None

    return user_id, amount, referrer_id


async def reject_deposit(deposit_id: int, reason: str | None = None) -> int | None:
    """Depozitni rad etadi. user_id qaytaradi."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_id, status FROM deposits WHERE id = $1", deposit_id
        )
        if not row or row["status"] in ("confirmed", "rejected"):
            return None
        await conn.execute(
            "UPDATE deposits SET status='rejected', reject_reason=$1 WHERE id=$2",
            reason, deposit_id,
        )
        return row["user_id"]


# ═══════════════════════════════════════════════════════════════
#  REFERAL
# ═══════════════════════════════════════════════════════════════

async def get_referrer(user_id: int) -> int | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT referred_by FROM users WHERE user_id = $1", user_id
        )
        return row["referred_by"] if row and row["referred_by"] else None


async def add_referral_earning(
    owner_id: int,
    from_user: int,
    amount: int,
    order_price: int,
    etype: str,
) -> None:
    """Referal daromad yozadi va balansga qo'shadi."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """INSERT INTO referral_earnings
                   (owner_id, from_user, amount, order_price, type, created_at)
                   VALUES ($1,$2,$3,$4,$5,$6)""",
                owner_id, from_user, amount, order_price, etype, int(time.time()),
            )
            await conn.execute(
                "UPDATE users SET balance = balance + $1 WHERE user_id = $2",
                amount, owner_id,
            )


async def get_referral_stats(user_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        invited = int((await conn.fetchrow(
            "SELECT COUNT(DISTINCT user_id) AS cnt FROM users WHERE referred_by = $1",
            user_id,
        ))["cnt"])
        total_earned = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) AS s FROM referral_earnings WHERE owner_id = $1",
            user_id,
        ))["s"])
        bonus_earned = int((await conn.fetchrow(
            """SELECT COALESCE(SUM(amount),0) AS s FROM referral_earnings
               WHERE owner_id=$1 AND type IN ('signup_bonus','deposit_bonus')""",
            user_id,
        ))["s"])
        percent_earned = int((await conn.fetchrow(
            """SELECT COALESCE(SUM(amount),0) AS s FROM referral_earnings
               WHERE owner_id=$1 AND type='percent'""",
            user_id,
        ))["s"])
    return {
        "invited":        invited,
        "total_earned":   total_earned,
        "bonus_earned":   bonus_earned,
        "percent_earned": percent_earned,
    }


async def get_referral_history(
    user_id: int, limit: int = 5, offset: int = 0
) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT re.*, u.full_name AS from_name, u.username AS from_username
               FROM referral_earnings re
               LEFT JOIN users u ON re.from_user = u.user_id
               WHERE re.owner_id = $1
               ORDER BY re.created_at DESC
               LIMIT $2 OFFSET $3""",
            user_id, limit, offset,
        )
        return [dict(r) for r in rows]


async def get_referral_history_count(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM referral_earnings WHERE owner_id = $1",
            user_id,
        )
        return int(row["cnt"])


# ═══════════════════════════════════════════════════════════════
#  ADMIN STATISTIKA
# ═══════════════════════════════════════════════════════════════

async def get_users_stats() -> dict:
    pool = await get_pool()
    now  = int(time.time())
    async with pool.acquire() as conn:
        total       = int((await conn.fetchrow("SELECT COUNT(*) AS cnt FROM users"))["cnt"])
        new_today   = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM users WHERE created_at >= $1", now - 86400))["cnt"])
        new_week    = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM users WHERE created_at >= $1", now - 604800))["cnt"])
        total_bal   = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(balance),0) AS s FROM users"))["s"])
        with_orders = int((await conn.fetchrow(
            "SELECT COUNT(DISTINCT user_id) AS cnt FROM orders"))["cnt"])
    return {
        "total":       total,
        "new_today":   new_today,
        "new_week":    new_week,
        "total_balance": total_bal,
        "with_orders": with_orders,
        "no_orders":   total - with_orders,
    }


async def get_orders_stats() -> dict:
    pool = await get_pool()
    now  = int(time.time())
    async with pool.acquire() as conn:
        total         = int((await conn.fetchrow("SELECT COUNT(*) AS cnt FROM orders"))["cnt"])
        total_rev     = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(price_uzs),0) AS s FROM orders"))["s"])
        today_orders  = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM orders WHERE created_at >= $1", now - 86400))["cnt"])
        today_rev     = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(price_uzs),0) AS s FROM orders WHERE created_at >= $1",
            now - 86400))["s"])
        completed     = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM orders WHERE status='Completed'"))["cnt"])
        pending       = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM orders WHERE status IN "
            "('Pending','In progress','Processing')"))["cnt"])
        canceled      = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM orders WHERE status IN ('Canceled','Cancelled')"))["cnt"])
    return {
        "total":         total,
        "total_revenue": total_rev,
        "today_orders":  today_orders,
        "today_revenue": today_rev,
        "completed":     completed,
        "pending":       pending,
        "canceled":      canceled,
    }


async def get_deposits_stats() -> dict:
    pool = await get_pool()
    now  = int(time.time())
    async with pool.acquire() as conn:
        p_count = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM deposits WHERE status='pending'"))["cnt"])
        p_sum   = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) AS s FROM deposits WHERE status='pending'"))["s"])
        c_sum   = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) AS s FROM deposits WHERE status='confirmed'"))["s"])
        t_conf  = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) AS s FROM deposits "
            "WHERE status='confirmed' AND confirmed_at >= $1", now - 86400))["s"])
    return {
        "pending_count":    p_count,
        "pending_sum":      p_sum,
        "confirmed_sum":    c_sum,
        "today_confirmed":  t_conf,
    }


async def get_top_users(limit: int = 10) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT u.user_id, u.full_name, u.username, u.balance,
                      COUNT(o.id) AS order_count,
                      COALESCE(SUM(o.price_uzs),0) AS total_spent
               FROM users u
               LEFT JOIN orders o ON u.user_id = o.user_id
               GROUP BY u.user_id, u.full_name, u.username, u.balance
               ORDER BY total_spent DESC
               LIMIT $1""",
            limit,
        )
        return [dict(r) for r in rows]
