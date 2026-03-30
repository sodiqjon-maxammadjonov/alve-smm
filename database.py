import asyncpg
import os
import time

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"), ssl="require")
    return _pool

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id      BIGINT PRIMARY KEY,
                username     TEXT,
                full_name    TEXT,
                balance      REAL    DEFAULT 0,
                referred_by  BIGINT  DEFAULT NULL,
                ref_bonus_given INTEGER DEFAULT 0,
                created_at   BIGINT  DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id             SERIAL PRIMARY KEY,
                user_id        BIGINT,
                smm_order_id   BIGINT,
                service_id     BIGINT,
                service_name   TEXT,
                platform       TEXT,
                link           TEXT,
                quantity       INTEGER,
                price_uzs      REAL,
                status         TEXT    DEFAULT 'Pending',
                created_at     BIGINT  DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id            SERIAL PRIMARY KEY,
                user_id       BIGINT,
                amount        REAL,
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
                amount      REAL,
                order_price REAL,
                type        TEXT,
                created_at  BIGINT  DEFAULT 0
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

async def get_balance(user_id: int) -> float:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
    return row["balance"] if row else 0.0

async def update_balance(user_id: int, amount: float):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET balance=balance+$1 WHERE user_id=$2", amount, user_id)

async def deduct_balance(user_id: int, amount: float) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
        if not row or row["balance"] < amount:
            return False
        await conn.execute("UPDATE users SET balance=balance-$1 WHERE user_id=$2", amount, user_id)
    return True

async def create_deposit(user_id: int, amount: float, check_file_id: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO deposits (user_id, amount, check_file_id, created_at) VALUES ($1,$2,$3,$4) RETURNING id",
            user_id, amount, check_file_id, int(time.time())
        )
        return row["id"]

async def get_pending_deposits():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT d.*, u.full_name FROM deposits d JOIN users u ON d.user_id=u.user_id WHERE d.status='pending' ORDER BY d.created_at DESC"
        )
    return [dict(r) for r in rows]

async def confirm_deposit(deposit_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():  # ← BU QO'SHILDI
            row = await conn.fetchrow("SELECT user_id, amount FROM deposits WHERE id=$1", deposit_id)
            if not row:
                return None
            user_id, amount = row["user_id"], row["amount"]
            await conn.execute(
                "UPDATE deposits SET status='confirmed', confirmed_at=$1 WHERE id=$2",
                int(time.time()), deposit_id
            )
            await conn.execute(
                "UPDATE users SET balance=balance+$1 WHERE user_id=$2", 
                amount, user_id
            )
    return user_id, amount

async def reject_deposit(deposit_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT user_id FROM deposits WHERE id=$1", deposit_id)
        if not row:
            return None
        await conn.execute("UPDATE deposits SET status='rejected' WHERE id=$1", deposit_id)
    return row["user_id"]

async def create_order(user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO orders (user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs, created_at)
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
        await conn.execute("UPDATE orders SET status=$1 WHERE smm_order_id=$2", status, smm_order_id)

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
    return row["cnt"] == 1

async def was_bonus_given(user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT ref_bonus_given FROM users WHERE user_id=$1", user_id)
    return bool(row["ref_bonus_given"]) if row else False

async def mark_bonus_given(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET ref_bonus_given=1 WHERE user_id=$1", user_id)

async def add_referral_earning(owner_id: int, from_user: int, amount: float, order_price: float, etype: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO referral_earnings (owner_id, from_user, amount, order_price, type, created_at) VALUES ($1,$2,$3,$4,$5,$6)",
            owner_id, from_user, amount, order_price, etype, int(time.time())
        )
        await conn.execute("UPDATE users SET balance=balance+$1 WHERE user_id=$2", amount, owner_id)

async def get_referral_stats(user_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        invited = (await conn.fetchrow("SELECT COUNT(DISTINCT user_id) as cnt FROM users WHERE referred_by=$1", user_id))["cnt"]
        total_earned = (await conn.fetchrow("SELECT COALESCE(SUM(amount),0) as s FROM referral_earnings WHERE owner_id=$1", user_id))["s"]
        bonus_earned = (await conn.fetchrow("SELECT COALESCE(SUM(amount),0) as s FROM referral_earnings WHERE owner_id=$1 AND type='bonus'", user_id))["s"]
        percent_earned = (await conn.fetchrow("SELECT COALESCE(SUM(amount),0) as s FROM referral_earnings WHERE owner_id=$1 AND type='percent'", user_id))["s"]
    return {
        "invited": invited,
        "total_earned": total_earned,
        "bonus_earned": bonus_earned,
        "percent_earned": percent_earned,
    }