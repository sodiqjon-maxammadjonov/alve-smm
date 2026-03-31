from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_referral_stats
from config import REFERRAL_PERCENT, REFERRAL_BONUS
import os

router = Router()

BOT_USERNAME = os.getenv("BOT_USERNAME", "zendor_smm_bot")

def referral_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🔗 Havolani ulashish",
        switch_inline_query=(
            f"🚀 Telegram va Instagram uchun eng arzon SMM xizmatlari!\n\n"
            f"✅ Minglab mijozlar ishongan panel\n"
            f"💰 Narxlar bozordan 5x arzon\n"
            f"⚡ Buyurtma bir zumda bajariladi\n"
            f"🎁 Ro'yxatdan o'tsangiz bonuslar kutmoqda!\n\n"
            f"👇 Hoziroq sinab ko'ring:\n"
            f"https://t.me/{BOT_USERNAME}?start=REF_{user_id}"
        )
    ))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()

@router.callback_query(F.data == "referral")
async def cb_referral(call: CallbackQuery):
    user_id = call.from_user.id
    stats = await get_referral_stats(user_id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{user_id}"

    await call.message.edit_text(
        "🎁 <b>Referal dasturi</b>\n\n"
        "Do'stlaringizni taklif qiling va ularning har bir buyurtmasidan daromad oling!\n\n"
        "💸 <b>Qanday ishlaydi?</b>\n"
        "├ Do'stingiz havolangiz orqali kiradi\n"
        f"├ Birinchi buyurtma bersa → sizga <b>+{REFERRAL_BONUS:,} so'm bonus</b>\n"
        f"└ Keyingi har buyurtmasidan → <b>{REFERRAL_PERCENT:.0f}% avtomatik balansga</b>\n\n"
        "📊 <b>Sizning statistikangiz:</b>\n"
        f"├ 👥 Taklif qilganlar: <b>{stats['invited']} kishi</b>\n"
        f"├ 🎁 Bonus daromad: <b>{stats['bonus_earned']:,.0f} so'm</b>\n"
        f"├ 💰 Foiz daromad: <b>{stats['percent_earned']:,.0f} so'm</b>\n"
        f"└ 📈 Jami daromad: <b>{stats['total_earned']:,.0f} so'm</b>\n\n"
        "🔗 <b>Sizning havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        "💡 Chegara yo'q — qancha ko'p odam, shuncha ko'p daromad! 🚀",
        reply_markup=referral_keyboard(user_id),
        parse_mode="HTML"
    )
    await call.answer()