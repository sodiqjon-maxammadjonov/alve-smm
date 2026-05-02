"""
database.py — Zendor SMM Bot
SQLite (aiosqlite) — tashqi server shart emas, fayl sifatida saqlanadi.
"""

import aiosqlite
import os
import re
import time

DB_PATH = os.getenv("DB_PATH", "zendor.db")


# ═══════════════════════════════════════════════════════════════
#  INIT
# ═══════════════════════════════════════════════════════════════

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id         INTEGER PRIMARY KEY,
                username        TEXT    DEFAULT '',
                full_name       TEXT    DEFAULT '',
                balance         INTEGER DEFAULT 0,
                referred_by     INTEGER DEFAULT NULL,
                ref_bonus_given INTEGER DEFAULT 0,
                discount        REAL    DEFAULT 0,
                banned          INTEGER DEFAULT 0,
                created_at      INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                smm_order_id  INTEGER,
                service_id    INTEGER,
                service_name  TEXT    DEFAULT '',
                platform      TEXT    DEFAULT '',
                link          TEXT    DEFAULT '',
                quantity      INTEGER DEFAULT 0,
                price_uzs     INTEGER DEFAULT 0,
                status        TEXT    DEFAULT 'Pending',
                created_at    INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                amount        INTEGER DEFAULT 0,
                status        TEXT    DEFAULT 'pending',
                check_file_id TEXT    DEFAULT '',
                reject_reason TEXT    DEFAULT NULL,
                created_at    INTEGER DEFAULT 0,
                confirmed_at  INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referral_earnings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id    INTEGER NOT NULL,
                from_user   INTEGER NOT NULL,
                amount      INTEGER DEFAULT 0,
                order_price INTEGER DEFAULT 0,
                type        TEXT    DEFAULT '',
                created_at  INTEGER DEFAULT 0
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_user   ON orders(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_deposits_user ON deposits(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_ref_owner     ON referral_earnings(owner_id)")
        await db.commit()


def _row(r) -> dict | None:
    return dict(r) if r else None

def _rows(rs) -> list:
    return [dict(r) for r in rs]

def _pg_to_sqlite(sql: str) -> str:
    """PostgreSQL $1,$2 → SQLite ? ga o'tkazadi."""
    return re.sub(r'\$\d+', '?', sql)

def _to_tuple(args):
    if not args:
        return ()
    if len(args) == 1:
        v = args[0]
        if isinstance(v, (list, tuple)):
            return tuple(v)
        return (v,)
    return tuple(args)


# ═══════════════════════════════════════════════════════════════
#  FOYDALANUVCHILAR
# ═══════════════════════════════════════════════════════════════

async def get_or_create_user(user_id: int, username: str, full_name: str,
                              referred_by: int | None = None) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT user_id FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        if row:
            await db.execute(
                "UPDATE users SET username=?, full_name=? WHERE user_id=?",
                (username or "", full_name or "", user_id)
            )
            await db.commit()
            return False
        await db.execute(
            "INSERT INTO users (user_id,username,full_name,referred_by,created_at) VALUES (?,?,?,?,?)",
            (user_id, username or "", full_name or "", referred_by, int(time.time()))
        )
        await db.commit()
        return True


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        return _row(await (await db.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)
        )).fetchone())


async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT balance FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        return int(row[0]) if row else 0


async def update_balance(user_id: int, amount: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def deduct_balance(user_id: int, amount: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT balance FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        if not row or int(row["balance"]) < amount:
            return False
        await db.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (amount, user_id))
        await db.commit()
        return True


async def set_balance(user_id: int, new_balance: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT balance FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        old = int(row["balance"]) if row else 0
        await db.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
        await db.commit()
        return old


async def get_user_discount(user_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT discount FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        return float(row[0]) if row else 0.0


async def set_user_discount(user_id: int, discount: float) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT user_id FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        if not row:
            return False
        await db.execute("UPDATE users SET discount=? WHERE user_id=?", (discount, user_id))
        await db.commit()
        return True


async def get_all_user_ids() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await (await db.execute("SELECT user_id FROM users")).fetchall()
        return [r[0] for r in rows]


# ═══════════════════════════════════════════════════════════════
#  BUYURTMALAR
# ═══════════════════════════════════════════════════════════════

async def create_order(user_id, smm_order_id, service_id, service_name,
                       platform, link, quantity, price_uzs) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO orders
               (user_id,smm_order_id,service_id,service_name,platform,link,quantity,price_uzs,created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs, int(time.time()))
        )
        await db.commit()
        return cur.lastrowid


async def get_user_orders(user_id: int, limit: int = 20) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )).fetchall()
        return _rows(rows)


async def update_order_status(smm_order_id: int, status: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE smm_order_id=?", (status, smm_order_id))
        await db.commit()


async def get_order_by_smm_id(smm_order_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        return _row(await (await db.execute(
            "SELECT * FROM orders WHERE smm_order_id=?", (smm_order_id,)
        )).fetchone())


async def get_active_orders(limit: int = 100) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(
            """SELECT * FROM orders
               WHERE status NOT IN ('Completed','Canceled','Cancelled','Refunded','Partial')
               ORDER BY created_at DESC LIMIT ?""", (limit,)
        )).fetchall()
        return _rows(rows)


async def get_all_orders_paginated(page=0, page_size=5, status_filter=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status_filter:
            rows = await (await db.execute(
                """SELECT o.*, u.full_name, u.username FROM orders o
                   JOIN users u ON o.user_id=u.user_id
                   WHERE o.status=? ORDER BY o.created_at DESC LIMIT ? OFFSET ?""",
                (status_filter, page_size, page * page_size)
            )).fetchall()
            total = (await (await db.execute(
                "SELECT COUNT(*) FROM orders WHERE status=?", (status_filter,)
            )).fetchone())[0]
        else:
            rows = await (await db.execute(
                """SELECT o.*, u.full_name, u.username FROM orders o
                   JOIN users u ON o.user_id=u.user_id
                   ORDER BY o.created_at DESC LIMIT ? OFFSET ?""",
                (page_size, page * page_size)
            )).fetchall()
            total = (await (await db.execute("SELECT COUNT(*) FROM orders")).fetchone())[0]
        return _rows(rows), total


# ═══════════════════════════════════════════════════════════════
#  DEPOZITLAR
# ═══════════════════════════════════════════════════════════════

async def create_deposit(user_id: int, amount: int, check_file_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO deposits (user_id,amount,check_file_id,created_at) VALUES (?,?,?,?)",
            (user_id, amount, check_file_id, int(time.time()))
        )
        await db.commit()
        return cur.lastrowid


async def get_deposit_status(deposit_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT status FROM deposits WHERE id=?", (deposit_id,)
        )).fetchone()
        return row[0] if row else None


async def get_pending_deposits() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(
            """SELECT d.*, u.full_name FROM deposits d
               JOIN users u ON d.user_id=u.user_id
               WHERE d.status='pending' ORDER BY d.created_at DESC"""
        )).fetchall()
        return _rows(rows)


async def confirm_deposit(deposit_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        dep = await (await db.execute(
            "SELECT user_id, amount, status FROM deposits WHERE id=?", (deposit_id,)
        )).fetchone()
        if not dep or dep["status"] == "confirmed":
            return None
        user_id = dep["user_id"]
        amount  = int(dep["amount"])
        await db.execute(
            "UPDATE deposits SET status='confirmed', confirmed_at=? WHERE id=?",
            (int(time.time()), deposit_id)
        )
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        ref = await (await db.execute(
            "SELECT referred_by FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        referrer_id = ref["referred_by"] if ref else None
        await db.commit()
    return user_id, amount, referrer_id


async def reject_deposit(deposit_id: int, reason: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT user_id, status FROM deposits WHERE id=?", (deposit_id,)
        )).fetchone()
        if not row or row["status"] in ("confirmed", "rejected"):
            return None
        await db.execute(
            "UPDATE deposits SET status='rejected', reject_reason=? WHERE id=?",
            (reason, deposit_id)
        )
        await db.commit()
        return row["user_id"]


# ═══════════════════════════════════════════════════════════════
#  REFERAL
# ═══════════════════════════════════════════════════════════════

async def get_referrer(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT referred_by FROM users WHERE user_id=?", (user_id,)
        )).fetchone()
        return row["referred_by"] if row and row["referred_by"] else None


async def add_referral_earning(owner_id, from_user, amount, order_price, etype):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO referral_earnings (owner_id,from_user,amount,order_price,type,created_at) VALUES (?,?,?,?,?,?)",
            (owner_id, from_user, amount, order_price, etype, int(time.time()))
        )
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, owner_id))
        await db.commit()


async def get_referral_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        invited        = (await (await db.execute("SELECT COUNT(DISTINCT user_id) FROM users WHERE referred_by=?", (user_id,))).fetchone())[0]
        total_earned   = (await (await db.execute("SELECT COALESCE(SUM(amount),0) FROM referral_earnings WHERE owner_id=?", (user_id,))).fetchone())[0]
        bonus_earned   = (await (await db.execute("SELECT COALESCE(SUM(amount),0) FROM referral_earnings WHERE owner_id=? AND type IN ('signup_bonus','deposit_bonus')", (user_id,))).fetchone())[0]
        percent_earned = (await (await db.execute("SELECT COALESCE(SUM(amount),0) FROM referral_earnings WHERE owner_id=? AND type='percent'", (user_id,))).fetchone())[0]
    return {
        "invited":        int(invited),
        "total_earned":   int(total_earned),
        "bonus_earned":   int(bonus_earned),
        "percent_earned": int(percent_earned),
    }


async def get_referral_history(user_id: int, limit: int = 5, offset: int = 0) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(
            """SELECT re.*, u.full_name AS from_name, u.username AS from_username
               FROM referral_earnings re
               LEFT JOIN users u ON re.from_user=u.user_id
               WHERE re.owner_id=? ORDER BY re.created_at DESC LIMIT ? OFFSET ?""",
            (user_id, limit, offset)
        )).fetchall()
        return _rows(rows)


async def get_referral_history_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT COUNT(*) FROM referral_earnings WHERE owner_id=?", (user_id,)
        )).fetchone()
        return int(row[0])


# ═══════════════════════════════════════════════════════════════
#  ADMIN STATISTIKA
# ═══════════════════════════════════════════════════════════════

async def get_users_stats() -> dict:
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        total       = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        new_today   = (await (await db.execute("SELECT COUNT(*) FROM users WHERE created_at>=?", (now-86400,))).fetchone())[0]
        new_week    = (await (await db.execute("SELECT COUNT(*) FROM users WHERE created_at>=?", (now-604800,))).fetchone())[0]
        total_bal   = (await (await db.execute("SELECT COALESCE(SUM(balance),0) FROM users")).fetchone())[0]
        with_orders = (await (await db.execute("SELECT COUNT(DISTINCT user_id) FROM orders")).fetchone())[0]
    return {
        "total":         int(total),
        "new_today":     int(new_today),
        "new_week":      int(new_week),
        "total_balance": int(total_bal),
        "with_orders":   int(with_orders),
        "no_orders":     int(total) - int(with_orders),
    }


async def get_orders_stats() -> dict:
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        total        = (await (await db.execute("SELECT COUNT(*) FROM orders")).fetchone())[0]
        total_rev    = (await (await db.execute("SELECT COALESCE(SUM(price_uzs),0) FROM orders")).fetchone())[0]
        today_orders = (await (await db.execute("SELECT COUNT(*) FROM orders WHERE created_at>=?", (now-86400,))).fetchone())[0]
        today_rev    = (await (await db.execute("SELECT COALESCE(SUM(price_uzs),0) FROM orders WHERE created_at>=?", (now-86400,))).fetchone())[0]
        completed    = (await (await db.execute("SELECT COUNT(*) FROM orders WHERE status='Completed'")).fetchone())[0]
        pending      = (await (await db.execute("SELECT COUNT(*) FROM orders WHERE status IN ('Pending','In progress','Processing')")).fetchone())[0]
        canceled     = (await (await db.execute("SELECT COUNT(*) FROM orders WHERE status IN ('Canceled','Cancelled')")).fetchone())[0]
    return {
        "total":         int(total),
        "total_revenue": int(total_rev),
        "today_orders":  int(today_orders),
        "today_revenue": int(today_rev),
        "completed":     int(completed),
        "pending":       int(pending),
        "canceled":      int(canceled),
    }


async def get_deposits_stats() -> dict:
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        p_count = (await (await db.execute("SELECT COUNT(*) FROM deposits WHERE status='pending'")).fetchone())[0]
        p_sum   = (await (await db.execute("SELECT COALESCE(SUM(amount),0) FROM deposits WHERE status='pending'")).fetchone())[0]
        c_sum   = (await (await db.execute("SELECT COALESCE(SUM(amount),0) FROM deposits WHERE status='confirmed'")).fetchone())[0]
        t_conf  = (await (await db.execute("SELECT COALESCE(SUM(amount),0) FROM deposits WHERE status='confirmed' AND confirmed_at>=?", (now-86400,))).fetchone())[0]
    return {
        "pending_count":   int(p_count),
        "pending_sum":     int(p_sum),
        "confirmed_sum":   int(c_sum),
        "today_confirmed": int(t_conf),
    }


async def get_top_users(limit: int = 10) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(
            """SELECT u.user_id, u.full_name, u.username, u.balance,
                      COUNT(o.id) AS order_count,
                      COALESCE(SUM(o.price_uzs),0) AS total_spent
               FROM users u LEFT JOIN orders o ON u.user_id=o.user_id
               GROUP BY u.user_id ORDER BY total_spent DESC LIMIT ?""", (limit,)
        )).fetchall()
        return _rows(rows)


# ═══════════════════════════════════════════════════════════════
#  get_pool — eski admin.py kodi uchun moslik adapteri
# ═══════════════════════════════════════════════════════════════

class _SqliteConn:
    """asyncpg Connection interfeysini SQLite ustiga quradi."""

    def __init__(self):
        self._db: aiosqlite.Connection | None = None

    async def __aenter__(self):
        self._db = await aiosqlite.connect(DB_PATH)
        self._db.row_factory = aiosqlite.Row
        await self._db.execute("PRAGMA journal_mode=WAL")
        return self

    async def __aexit__(self, *_):
        if self._db:
            await self._db.commit()
            await self._db.close()

    @staticmethod
    def _fix(sql: str, args) -> tuple:
        sql = re.sub(r'\$\d+', '?', sql)
        if not args:
            return sql, ()
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return sql, tuple(args[0])
        return sql, tuple(args)

    async def execute(self, sql: str, *args):
        sql, params = self._fix(sql, args)
        await self._db.execute(sql, params)

    async def fetchrow(self, sql: str, *args):
        sql, params = self._fix(sql, args)
        return await (await self._db.execute(sql, params)).fetchone()

    async def fetch(self, sql: str, *args):
        sql, params = self._fix(sql, args)
        return await (await self._db.execute(sql, params)).fetchall()

    # transaction() — SQLite autocommit ishlatadi, shunchaki self qaytaramiz
    def transaction(self):
        return _NullCtx()


class _NullCtx:
    async def __aenter__(self): return self
    async def __aexit__(self, *_): pass


class _FakePool:
    def acquire(self):
        return _SqliteConn()


_fake_pool = _FakePool()


async def get_pool():
    """Eski admin.py kodi uchun — SQLite adapter qaytaradi."""
    return _fake_pool