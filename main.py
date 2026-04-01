import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from config import BOT_TOKEN, ADMIN_ID
from database import init_db
from handlers import start, balance, services, orders, support, group, referral, broadcast, admin
from handlers.orders import auto_update_orders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


async def set_bot_commands(bot: Bot):
    user_commands = [
        BotCommand(command="start",       description="Botni ishga tushirish"),
        BotCommand(command="commandlist", description="Komandalar royxati"),
        BotCommand(command="balans",      description="Balansni korish"),
        BotCommand(command="xizmatlar",   description="Xizmatlar royxati"),
        BotCommand(command="buyurtmalar", description="Buyurtmalarim"),
        BotCommand(command="referral",    description="Referal dasturi"),
        BotCommand(command="yordam",      description="Yordam"),
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    admin_commands = user_commands + [
        BotCommand(command="admin",         description="Admin panel"),
        BotCommand(command="stats",         description="Statistika"),
        BotCommand(command="users",         description="Foydalanuvchilar"),
        BotCommand(command="pending",       description="Kutayotgan depozitlar"),
        BotCommand(command="top",           description="Top 10 mijozlar"),
        BotCommand(command="broadcast",     description="Hammaga xabar"),
        BotCommand(command="balance_check", description="Balans tekshirish"),
        BotCommand(command="add_balance",   description="Balans qoshish"),
    ]
    try:
        await bot.set_my_commands(
            admin_commands,
            scope=BotCommandScopeChat(chat_id=ADMIN_ID)
        )
    except Exception as e:
        logging.warning(f"Admin commands set failed: {e}")


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await set_bot_commands(bot)

    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(services.router)
    dp.include_router(orders.router)
    dp.include_router(support.router)
    dp.include_router(group.router)
    dp.include_router(referral.router)
    dp.include_router(broadcast.router)

    # Har 5 daqiqada order statuslarini yangilaydi
    asyncio.create_task(auto_update_orders(bot))

    logging.info("Bot ishga tushdi! Auto-updater yoqildi.")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())