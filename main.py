"""
main.py — Zendor SMM Bot
Bot entry point. Barcha routerlar shu yerda ro'yxatga olinadi.

YANGI HANDLER QO'SHISH:
  1. handlers/ papkasiga yangi fayl oching
  2. Router yarating: router = Router()
  3. Quyida import qiling va dp.include_router() ga qo'shing
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from config import BOT_TOKEN, ADMIN_IDS, ADMIN_ID
from database import init_db

# Handler importlari
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


# ── Bot komandalar ro'yxati ───────────────────────────────────

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
    BotCommand(command="admin",        description="🛠 Admin panel"),
    BotCommand(command="stats",        description="📊 Statistika"),
    BotCommand(command="userinfo",     description="👤 User ma'lumoti"),
    BotCommand(command="userorders",   description="📦 User buyurtmalari"),
    BotCommand(command="userstats",    description="📊 User statistikasi"),
    BotCommand(command="add_balance",  description="➕ Balans qo'shish"),
    BotCommand(command="set_balance",  description="🔧 Balans o'rnatish"),
    BotCommand(command="discount",     description="🏷 Chegirma o'rnatish"),
    BotCommand(command="ban",          description="⛔ Bloklash"),
    BotCommand(command="unban",        description="✅ Blokni ochish"),
    BotCommand(command="pending",      description="⏳ Kutayotgan depozitlar"),
    BotCommand(command="top",          description="🏆 Top 10 mijozlar"),
    BotCommand(command="smm_balance",  description="💵 SMM panel balansi"),
    BotCommand(command="broadcast",    description="📢 Broadcast"),
    BotCommand(command="groupid",      description="🆔 Guruh ID"),
]


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            logger.warning(f"Admin commands set failed for {admin_id}: {e}")


# ── Asosiy funksiya ───────────────────────────────────────────

async def main() -> None:
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    await set_bot_commands(bot)

    # Router tartibi muhim — admin birinchi bo'lishi kerak
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(services.router)
    dp.include_router(orders.router)
    dp.include_router(support.router)
    dp.include_router(group.router)
    dp.include_router(broadcast.router)

    # Background task — har 5 daqiqada order statuslarini yangilaydi
    asyncio.create_task(auto_update_orders(bot))

    logger.info("✅ Zendor SMM Bot ishga tushdi!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
