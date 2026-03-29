from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.menus import back_to_main
import os

router = Router()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "your_admin_username")

def support_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👨‍💼 Admin bilan bog'lanish", url=f"https://t.me/@smo_2811"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()

@router.callback_query(F.data == "support")
async def cb_support(call: CallbackQuery):
    await call.message.edit_text(
        "🆘 <b>Yordam</b>\n\n"
        "Savol yoki muammolaringiz bo'lsa admin bilan bog'laning 👇\n\n"
        "📌 <b>Ko'p so'raladigan savollar:</b>\n\n"
        "❓ <b>Buyurtma qancha vaqtda bajariladi?</b>\n"
        "➡️ Hizmatga qarab 1 daqiqadan bir necha soatgacha\n\n"
        "❓ <b>Balans qanday to'ldiriladi?</b>\n"
        "➡️ Kartaga o'tkazma orqali, chek 5 daqiqada tasdiqlanadi\n\n"
        "❓ <b>Buyurtma bajarilmasa pul qaytadimi?</b>\n"
        "➡️ Ha, bajarilmagan qismi balansingizga qaytariladi\n\n"
        "❓ <b>Minimal to'ldirish summasi qancha?</b>\n"
        "➡️ 5,000 so'mdan boshlanadi",
        reply_markup=support_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()