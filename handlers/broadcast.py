"""
handlers/broadcast.py — Zendor SMM Bot
Barcha foydalanuvchilarga xabar yuborish.
"""

import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_all_user_ids
from config import ADMIN_IDS
from keyboards.menus import back_to_main, admin_panel_keyboard

router   = Router()
logger   = logging.getLogger(__name__)


class BroadcastState(StatesGroup):
    waiting_message  = State()
    waiting_confirm  = State()


@router.message(Command("broadcast"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_broadcast(message: Message, state: FSMContext):
    await state.set_state(BroadcastState.waiting_message)
    await message.answer(
        "📢 <b>Broadcast</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni yuboring.\n\n"
        "Bekor qilish: /cancel",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_broadcast", F.from_user.id.in_(ADMIN_IDS))
async def cb_broadcast(call: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastState.waiting_message)
    await call.message.answer(
        "📢 <b>Broadcast</b>\n\n"
        "Xabarni yuboring. Bekor qilish: /cancel",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(Command("cancel"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Bekor qilindi.", reply_markup=admin_panel_keyboard())


@router.message(BroadcastState.waiting_message, F.from_user.id.in_(ADMIN_IDS))
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_ids = await get_all_user_ids()
    total    = len(user_ids)

    status_msg = await message.answer(
        f"⏳ Yuborilmoqda... <b>0 / {total}</b>", parse_mode="HTML"
    )
    sent, failed = 0, 0

    for i, uid in enumerate(user_ids):
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            sent += 1
        except Exception as e:
            logger.debug(f"Broadcast skip {uid}: {e}")
            failed += 1

        if (i + 1) % 25 == 0:
            try:
                await status_msg.edit_text(
                    f"⏳ Yuborilmoqda... <b>{i+1} / {total}</b>",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            await asyncio.sleep(0.5)

        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ <b>Broadcast tugadi!</b>\n\n"
        f"├ 📨 Yuborildi: <b>{sent}</b>\n"
        f"└ ❌ Xato:      <b>{failed}</b> (bloklagan/o'chirilgan)",
        parse_mode="HTML",
    )
