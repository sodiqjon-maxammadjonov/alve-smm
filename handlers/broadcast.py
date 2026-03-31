import asyncio
import logging
import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_pool

router = Router()
logger = logging.getLogger(__name__)

ADMIN_IDS = [int(os.getenv("ADMIN_ID", 7917217047))]


class BroadcastState(StatesGroup):
    waiting_message = State()


async def get_all_user_ids() -> list[int]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
    return [row["user_id"] for row in rows]


@router.message(Command("broadcast"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_broadcast(message: Message, state: FSMContext):
    await message.answer(
        "📢 <b>Broadcast</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing.\n\n"
        "Bekor qilish uchun: /cancel",
        parse_mode="HTML"
    )
    await state.set_state(BroadcastState.waiting_message)


@router.message(Command("cancel"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Bekor qilindi.")


@router.message(BroadcastState.waiting_message, F.from_user.id.in_(ADMIN_IDS))
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_ids = await get_all_user_ids()
    total = len(user_ids)

    status_msg = await message.answer(f"⏳ Yuborilmoqda... 0/{total}")

    sent = 0
    failed = 0

    for i, user_id in enumerate(user_ids):
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            sent += 1
        except Exception as e:
            logger.warning(f"Broadcast failed for {user_id}: {e}")
            failed += 1

        if (i + 1) % 20 == 0:
            await status_msg.edit_text(f"⏳ Yuborilmoqda... {i + 1}/{total}")
            await asyncio.sleep(0.5)

        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ <b>Broadcast tugadi!</b>\n\n"
        f"├ 📨 Yuborildi: <b>{sent}</b>\n"
        f"└ ❌ Xato: <b>{failed}</b> (bloklagan yoki o'chirilgan)",
        parse_mode="HTML"
    )