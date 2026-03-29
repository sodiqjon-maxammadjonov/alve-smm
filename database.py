import aiosqlite
import time

DB_PATH = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id      INTEGER PRIMARY KEY,
                username     TEXT,
                full_name    TEXT,
                balance      REAL    DEFAULT 0,
                referred_by  INTEGER DEFAULT NULL,
                ref_bonus_given INTEGER DEFAULT 0,
                created_at   INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER,
                smm_order_id   INTEGER,
                service_id     INTEGER,
                service_name   TEXT,
                platform       TEXT,
                link           TEXT,
                quantity       INTEGER,
                price_uzs      REAL,
                status         TEXT    DEFAULT 'Pending',
                created_at     INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER,
                amount        REAL,
                status        TEXT    DEFAULT 'pending',
                check_file_id TEXT,
                created_at    INTEGER DEFAULT 0,
                confirmed_at  INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referral_earnings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id    INTEGER,
                from_user   INTEGER,
                amount      REAL,
                order_price REAL,
                type        TEXT,
                created_at  INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def get_or_create_user(user_id: int, username: str, full_name: str, referred_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            await db.execute(
                "INSERT INTO users (user_id, username, full_name, referred_by, created_at) VALUES (?,?,?,?,?)",
                (user_id, username, full_name, referred_by, int(time.time()))
            )
            await db.commit()

async def get_balance(user_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    return row[0] if row else 0.0

async def update_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def deduct_balance(user_id: int, amount: float) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < amount:
            return False
        await db.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (amount, user_id))
        await db.commit()
    return True

async def create_deposit(user_id: int, amount: float, check_file_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO deposits (user_id, amount, check_file_id, created_at) VALUES (?,?,?,?)",
            (user_id, amount, check_file_id, int(time.time()))
        )
        await db.commit()
        return cur.lastrowid

async def get_pending_deposits():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT d.*, u.full_name FROM deposits d JOIN users u ON d.user_id=u.user_id WHERE d.status='pending' ORDER BY d.created_at DESC"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

async def confirm_deposit(deposit_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id, amount FROM deposits WHERE id=?", (deposit_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        user_id, amount = row
        await db.execute(
            "UPDATE deposits SET status='confirmed', confirmed_at=? WHERE id=?",
            (int(time.time()), deposit_id)
        )
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        await db.commit()
        return user_id, amount

async def reject_deposit(deposit_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM deposits WHERE id=?", (deposit_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        await db.execute("UPDATE deposits SET status='rejected' WHERE id=?", (deposit_id,))
        await db.commit()
        return row[0]

async def create_order(user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO orders (user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (user_id, smm_order_id, service_id, service_name, platform, link, quantity, price_uzs, int(time.time()))
        )
        await db.commit()
        return cur.lastrowid

async def get_user_orders(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

async def update_order_status(smm_order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE smm_order_id=?", (status, smm_order_id))
        await db.commit()

async def get_order_by_smm_id(smm_order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders WHERE smm_order_id=?", (smm_order_id,)) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None

async def get_referrer(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT referred_by FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    return row[0] if row and row[0] else None

async def is_first_order(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
    return row[0] == 1

async def was_bonus_given(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT ref_bonus_given FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    return bool(row[0]) if row else False

async def mark_bonus_given(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET ref_bonus_given=1 WHERE user_id=?", (user_id,))
        await db.commit()

async def add_referral_earning(owner_id: int, from_user: int, amount: float, order_price: float, etype: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO referral_earnings (owner_id, from_user, amount, order_price, type, created_at) VALUES (?,?,?,?,?,?)",
            (owner_id, from_user, amount, order_price, etype, int(time.time()))
        )
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, owner_id))
        await db.commit()

async def get_referral_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM users WHERE referred_by=?", (user_id,)
        ) as cur:
            invited = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COALESCE(SUM(amount),0) FROM referral_earnings WHERE owner_id=?", (user_id,)
        ) as cur:
            total_earned = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COALESCE(SUM(amount),0) FROM referral_earnings WHERE owner_id=? AND type='bonus'", (user_id,)
        ) as cur:
            bonus_earned = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COALESCE(SUM(amount),0) FROM referral_earnings WHERE owner_id=? AND type='percent'", (user_id,)
        ) as cur:
            percent_earned = (await cur.fetchone())[0]
    return {
        "invited": invited,
        "total_earned": total_earned,
        "bonus_earned": bonus_earned,
        "percent_earned": percent_earned,
    }