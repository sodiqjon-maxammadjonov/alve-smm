"""
handlers/support.py — Zendor SMM Bot
"""
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from keyboards.menus import support_keyboard
from core.constants import DIVIDER

router = Router()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")


def _support_text() -> str:
    return (
        f"🆘 <b>Yordam markazi</b>\n\n"
        f"{DIVIDER}\n"
        "❓ <b>Buyurtma qancha vaqtda bajariladi?</b>\n"
        "➡️ Xizmatga qarab 1 daqiqadan bir necha soatgacha\n\n"
        "❓ <b>Balans qanday to'ldiriladi?</b>\n"
        "➡️ Kartaga o'tkazma — chek 5 daqiqada tasdiqlanadi\n\n"
        "❓ <b>Buyurtma bajarilmasa pul qaytadimi?</b>\n"
        "➡️ Ha, bajarilmagan qism balansingizga avtomatik qaytadi\n\n"
        "❓ <b>Minimal to'ldirish summasi?</b>\n"
        "➡️ 5 000 so'mdan boshlanadi\n\n"
        "❓ <b>Refill qanday ishlaydi?</b>\n"
        "➡️ ♻️ belgili xizmatlar tushib ketsa, bepul to'ldiriladi\n\n"
        f"{DIVIDER}\n"
        "💬 Boshqa savollar uchun admin bilan bog'laning 👇"
    )


@router.callback_query(F.data == "support")
async def cb_support(call: CallbackQuery):
    await call.message.edit_text(
        _support_text(),
        reply_markup=support_keyboard(ADMIN_USERNAME),
        parse_mode="HTML",
    )
    await call.answer()


@router.message(Command("yordam"))
async def cmd_yordam(message: Message):
    await message.answer(
        _support_text(),
        reply_markup=support_keyboard(ADMIN_USERNAME),
        parse_mode="HTML",
    )
