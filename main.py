"""
main.py — Zendor SMM Bot
Render.com Web Service + SQLite + self-ping (24/7) + avtomatik backup
"""

import asyncio
import logging
import os
from datetime import datetime, time as dtime, timedelta

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from config import BOT_TOKEN, ADMIN_IDS, ADMIN_ID
from database import init_db

from handlers import (
    start, balance, services, orders,
    support, group, broadcast, admin,
)
from handlers.orders import auto_update_orders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "zendor.db")


# ─── BOT KOMANDALAR ────────────────────────────────────────────

USER_COMMANDS = [
    BotCommand(command="start",       description="🚀 Botni ishga tushirish"),
    BotCommand(command="commandlist", description="📋 Barcha komandalar"),
    BotCommand(command="balans",      description="💰 Balansingiz"),
    BotCommand(command="xizmatlar",   description="🛍 Xizmatlar"),
    BotCommand(command="buyurtmalar", description="📦 Buyurtmalarim"),
    BotCommand(command="referral",    description="🎁 Referal dasturi"),
    BotCommand(command="yordam",      description="🆘 Yordam"),
]

ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(command="admin",           description="🛠 Admin panel"),
    BotCommand(command="stats",           description="📊 Statistika"),
    BotCommand(command="userinfo",        description="👤 User ma'lumoti"),
    BotCommand(command="userorders",      description="📦 User buyurtmalari"),
    BotCommand(command="userstats",       description="📊 User statistikasi"),
    BotCommand(command="add_balance",     description="➕ Balans qo'shish"),
    BotCommand(command="set_balance",     description="🔧 Balans o'rnatish"),
    BotCommand(command="set_balance_mute",description="🔇 Balans o'rnatish (xabarsiz)"),
    BotCommand(command="discount",        description="🏷 Chegirma o'rnatish"),
    BotCommand(command="ban",             description="⛔ Bloklash"),
    BotCommand(command="unban",           description="✅ Blokni ochish"),
    BotCommand(command="pending",         description="⏳ Kutayotgan depozitlar"),
    BotCommand(command="top",             description="🏆 Top 10 mijozlar"),
    BotCommand(command="smm_balance",     description="💵 SMM panel balansi"),
    BotCommand(command="broadcast",       description="📢 Broadcast"),
    BotCommand(command="backup",          description="🗄 DB backup olish"),
    BotCommand(command="groupid",         description="🆔 Guruh ID"),
]


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANDS,
                scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            logger.warning(f"Admin commands set failed for {admin_id}: {e}")


# ─── HEALTH CHECK ──────────────────────────────────────────────

async def health_check(request):
    return web.Response(text="OK ✅", status=200)


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    port = int(os.getenv("PORT", 10000))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"Health check server: port {port} ✅")
    return runner


# ─── SELF-PING ─────────────────────────────────────────────────

async def self_ping():
    """Har 14 daqiqada o'ziga ping yuboradi."""
    import aiohttp

    render_url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")

    if not render_url:
        logger.warning("RENDER_EXTERNAL_URL yo'q — self-ping o'chirilgan")
        return

    await asyncio.sleep(60)

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{render_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as r:
                    logger.info(f"Self-ping: {r.status}")
        except Exception as e:
            logger.warning(f"Self-ping xato: {e}")

        await asyncio.sleep(14 * 60)


# ─── BACKUP ────────────────────────────────────────────────────

async def send_backup(bot: Bot, requester_id: int | None = None):
    """DB faylini GROUP_ID ga yuboradi."""
    group_id = os.getenv("GROUP_ID") or str(ADMIN_ID)

    try:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")

        # ✅ SAFE LOGIC (f-string ichida emas)
        status_text = (
            "👤 Admin tomonidan so'raldi"
            if requester_id
            else "⏰ Avtomatik (kunlik)"
        )

        caption = (
            f"🗄 <b>Zendor SMM — Backup</b>\n"
            f"📅 {now}\n"
            f"{status_text}"
        )

        with open(DB_PATH, "rb") as f:
            await bot.send_document(
                chat_id=group_id,
                document=f,
                filename=f"zendor_backup_{now}.db",
                caption=caption,
                parse_mode="HTML",
            )

        logger.info(f"Backup yuborildi → {group_id}")
        return True

    except Exception as e:
        logger.error(f"Backup xato: {e}")
        return False


async def daily_backup_scheduler(bot: Bot):
    """Har kuni 00:00 da backup."""
    while True:
        now = datetime.now()
        next_midnight = datetime.combine(now.date(), dtime(0, 0)) + timedelta(days=1)

        wait_secs = (next_midnight - now).total_seconds()

        logger.info(
            f"Keyingi backup: {int(wait_secs/3600)} soat "
            f"{int((wait_secs%3600)/60)} daqiqa"
        )

        await asyncio.sleep(wait_secs)
        await send_backup(bot)


# ─── MAIN ──────────────────────────────────────────────────────

async def main() -> None:
    await init_db()
    logger.info("SQLite database tayyor ✅")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await set_bot_commands(bot)

    # Router order muhim
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(services.router)
    dp.include_router(orders.router)
    dp.include_router(support.router)
    dp.include_router(group.router)
    dp.include_router(broadcast.router)

    runner = await start_web_server()

    # Background tasks
    asyncio.create_task(auto_update_orders(bot))
    asyncio.create_task(daily_backup_scheduler(bot))
    asyncio.create_task(self_ping())

    logger.info("✅ Zendor SMM Bot ishga tushdi!")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())     