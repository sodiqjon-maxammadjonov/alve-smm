import asyncpg
import os
import time

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"), ssl="require", min_size=2, max_size=10)
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id         BIGINT  PRIMARY KEY,
                username        TEXT,
                full_name       TEXT,
                balance         BIGINT  DEFAULT 0,
                referred_by     BIGINT  DEFAULT NULL,
                ref_bonus_given INTEGER DEFAULT 0,
                created_at      BIGINT  DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id            SERIAL  PRIMARY KEY,
                user_id       BIGINT,
                smm_order_id  BIGINT,
                service_id    BIGINT,
                service_name  TEXT,
                platform      TEXT,
                link          TEXT,
                quantity      INTEGER,
                price_uzs     BIGINT,
                status        TEXT    DEFAULT 'Pending',
                created_at    BIGINT  DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id            SERIAL  PRIMARY KEY,
                user_id       BIGINT,
                amount        BIGINT,
                status        TEXT    DEFAULT 'pending',
                check_file_id TEXT,
                created_at    BIGINT  DEFAULT 0,
                confirmed_at  BIGINT  DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS referral_earnings (
                id          SERIAL PRIMARY KEY,
                owner_id    BIGINT,
                from_user   BIGINT,
                amount      BIGINT,
                order_price BIGINT,
                type        TEXT,
                created_at  BIGINT DEFAULT 0
            )
        """)


async def get_or_create_user(user_id: int, username: str, full_name: str, referred_by: int = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT user_id FROM users WHERE user_id=$1", user_id)
        if not row:
            await conn.execute(
                "INSERT INTO users (user_id, username, full_name, referred_by, created_at) VALUES ($1,$2,$3,$4,$5)",
                user_id, username, full_name, referred_by, int(time.time())
            )


async def get_balance(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
        return int(row["balance"]) if row else 0


async def update_balance(user_id: int, amount: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = balance + $1 WHERE user_id = $2",
            amount, user_id
        )


async def deduct_balance(user_id: int, amount: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT balance FROM users WHERE user_id=$1 FOR UPDATE", user_id
            )
            if not row or int(row["balance"]) < amount:
                return False
            await conn.execute(
                "UPDATE users SET balance = balance - $1 WHERE user_id = $2",
                amount, user_id
            )
    return True


async def create_deposit(user_id: int, amount: int, check_file_id: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO deposits (user_id, amount, check_file_id, created_at) VALUES ($1,$2,$3,$4) RETURNING id",
            user_id, amount, check_file_id, int(time.time())
        )
        return row["id"]


async def get_deposit_status(deposit_id: int) -> str | None:
    """Deposit statusini qaytaradi: 'pending', 'confirmed', 'rejected' yoki None"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT status FROM deposits WHERE id=$1", deposit_id)
        return row["status"] if row else None


async def get_pending_deposits():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT d.*, u.full_name FROM deposits d "
            "JOIN users u ON d.user_id = u.user_id "
            "WHERE d.status = 'pending' ORDER BY d.created_at DESC"
        )
        return [dict(r) for r in rows]


async def confirm_deposit(deposit_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT user_id, amount, status FROM deposits WHERE id=$1 FOR UPDATE",
                deposit_id
            )
            if not row:
                return None
            if row["status"] == "confirmed":
                return None
            user_id = row["user_id"]
            amount = int(row["amount"])
            await conn.execute(
                "UPDATE deposits SET status='confirmed', confirmed_at=$1 WHERE id=$2",
                int(time.time()), deposit_id
            )
            await conn.execute(
                "INSERT INTO users (user_id, balance, created_at) VALUES ($1, 0, $2) ON CONFLICT (user_id) DO NOTHING",
                user_id, int(time.time())
            )
            await conn.execute(
                "UPDATE users SET balance = balance + $1 WHERE user_id = $2",
                amount, user_id
            )
            return user_id, amount


async def reject_deposit(deposit_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT user_id, status FROM deposits WHERE id=$1 FOR UPDATE", deposit_id
            )
            if not row or row["status"] == "rejected":
                return None
            await conn.execute(
                "UPDATE deposits SET status='rejected' WHERE id=$1", deposit_id
            )
    return row["user_id"]


async def create_order(user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO orders
               (user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs, created_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9) RETURNING id""",
            user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs, int(time.time())
        )
        return row["id"]


async def get_user_orders(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM orders WHERE user_id=$1 ORDER BY created_at DESC LIMIT 20", user_id
        )
        return [dict(r) for r in rows]


async def update_order_status(smm_order_id: int, status: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE orders SET status=$1 WHERE smm_order_id=$2", status, smm_order_id
        )


async def get_order_by_smm_id(smm_order_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM orders WHERE smm_order_id=$1", smm_order_id)
        return dict(row) if row else None


async def get_referrer(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT referred_by FROM users WHERE user_id=$1", user_id)
        return row["referred_by"] if row and row["referred_by"] else None


async def is_first_order(user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT COUNT(*) as cnt FROM orders WHERE user_id=$1", user_id)
        return int(row["cnt"]) == 1


async def was_bonus_given(user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT ref_bonus_given FROM users WHERE user_id=$1", user_id)
        return bool(row["ref_bonus_given"]) if row else False


async def mark_bonus_given(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET ref_bonus_given=1 WHERE user_id=$1", user_id)


async def add_referral_earning(owner_id: int, from_user: int, amount: int, order_price: int, etype: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO referral_earnings (owner_id, from_user, amount, order_price, type, created_at) "
                "VALUES ($1,$2,$3,$4,$5,$6)",
                owner_id, from_user, amount, order_price, etype, int(time.time())
            )
            await conn.execute(
                "UPDATE users SET balance = balance + $1 WHERE user_id = $2",
                amount, owner_id
            )


async def get_referral_stats(user_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        invited = int((await conn.fetchrow(
            "SELECT COUNT(DISTINCT user_id) as cnt FROM users WHERE referred_by=$1", user_id
        ))["cnt"])
        total_earned = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) as s FROM referral_earnings WHERE owner_id=$1", user_id
        ))["s"])
        bonus_earned = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) as s FROM referral_earnings WHERE owner_id=$1 AND type='bonus'", user_id
        ))["s"])
        percent_earned = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) as s FROM referral_earnings WHERE owner_id=$1 AND type='percent'", user_id
        ))["s"])
    return {
        "invited": invited,
        "total_earned": total_earned,
        "bonus_earned": bonus_earned,
        "percent_earned": percent_earned,
    }


# ── Admin statistika funksiyalari ─────────────────────────────

async def get_users_stats() -> dict:
    """Foydalanuvchilar statistikasi"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        total = int((await conn.fetchrow("SELECT COUNT(*) as cnt FROM users"))["cnt"])
        today_ts = int(time.time()) - 86400
        new_today = int((await conn.fetchrow(
            "SELECT COUNT(*) as cnt FROM users WHERE created_at >= $1", today_ts
        ))["cnt"])
        week_ts = int(time.time()) - 604800
        new_week = int((await conn.fetchrow(
            "SELECT COUNT(*) as cnt FROM users WHERE created_at >= $1", week_ts
        ))["cnt"])
        total_balance = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(balance),0) as s FROM users"
        ))["s"])
        with_orders = int((await conn.fetchrow(
            "SELECT COUNT(DISTINCT user_id) as cnt FROM orders"
        ))["cnt"])
    return {
        "total": total,
        "new_today": new_today,
        "new_week": new_week,
        "total_balance": total_balance,
        "with_orders": with_orders,
        "no_orders": total - with_orders,
    }


async def get_orders_stats() -> dict:
    """Buyurtmalar statistikasi"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        total = int((await conn.fetchrow("SELECT COUNT(*) as cnt FROM orders"))["cnt"])
        total_revenue = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(price_uzs),0) as s FROM orders"
        ))["s"])
        today_ts = int(time.time()) - 86400
        today_orders = int((await conn.fetchrow(
            "SELECT COUNT(*) as cnt FROM orders WHERE created_at >= $1", today_ts
        ))["cnt"])
        today_revenue = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(price_uzs),0) as s FROM orders WHERE created_at >= $1", today_ts
        ))["s"])
        completed = int((await conn.fetchrow(
            "SELECT COUNT(*) as cnt FROM orders WHERE status='Completed'"
        ))["cnt"])
        pending = int((await conn.fetchrow(
            "SELECT COUNT(*) as cnt FROM orders WHERE status IN ('Pending','In progress','Processing')"
        ))["cnt"])
    return {
        "total": total,
        "total_revenue": total_revenue,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "completed": completed,
        "pending": pending,
    }


async def get_deposits_stats() -> dict:
    """Depozitlar statistikasi"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        pending_count = int((await conn.fetchrow(
            "SELECT COUNT(*) as cnt FROM deposits WHERE status='pending'"
        ))["cnt"])
        pending_sum = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) as s FROM deposits WHERE status='pending'"
        ))["s"])
        confirmed_sum = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) as s FROM deposits WHERE status='confirmed'"
        ))["s"])
        today_ts = int(time.time()) - 86400
        today_confirmed = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) as s FROM deposits WHERE status='confirmed' AND confirmed_at >= $1",
            today_ts
        ))["s"])
    return {
        "pending_count": pending_count,
        "pending_sum": pending_sum,
        "confirmed_sum": confirmed_sum,
        "today_confirmed": today_confirmed,
    }


async def get_top_users(limit: int = 10) -> list:
    """Eng ko'p xarid qilgan foydalanuvchilar"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT u.user_id, u.full_name, u.username, u.balance,
                      COUNT(o.id) as order_count,
                      COALESCE(SUM(o.price_uzs),0) as total_spent
               FROM users u
               LEFT JOIN orders o ON u.user_id = o.user_id
               GROUP BY u.user_id, u.full_name, u.username, u.balance
               ORDER BY total_spent DESC
               LIMIT $1""",
            limit
        )
        return [dict(r) for r in rows]