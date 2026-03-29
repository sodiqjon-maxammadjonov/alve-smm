from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_or_create_user, get_balance, get_user_orders
from keyboards.menus import main_menu, main_reply_keyboard, back_to_main, services_menu
import os
import aiosqlite

router = Router()

BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")

WELCOME_TEXT = (
    "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
    "🚀 <b>Zendor SMM bot</b>ga xush kelibsiz!\n\n"
    "Bu bot orqali siz Telegram va Instagram uchun\n"
    "arzon SMM xizmatlarini sotib olishingiz mumkin.\n\n"
    "Quyidagi menyudan tanlang:"
)

REPLY_TO_CALLBACK = {
    "📦 Xizmatlar":    "services",
    "💰 Balans":       "balance",
    "🗂 Buyurtmalarim": "my_orders",
    "ℹ️ Yordam":       "support",
    "🎁 Referal":      "referral",
}

class RefCodeState(StatesGroup):
    waiting_code = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    args = message.text.split()
    referred_by = None

    if len(args) > 1:
        param = args[1]
        if param.startswith("REF_"):
            try:
                ref_id = int(param.replace("REF_", ""))
                if ref_id != message.from_user.id:
                    referred_by = ref_id
            except ValueError:
                pass

    await get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
        referred_by=referred_by
    )
    await state.clear()

    if referred_by:
        await message.answer(
            "🎁 Siz do'stingizning taklifi orqali kirdingiz!\n"
            "Birinchi buyurtmangizdan so'ng do'stingiz <b>500 so'm bonus</b> oladi.\n\n"
            + WELCOME_TEXT.format(name=message.from_user.first_name),
            reply_markup=main_reply_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            WELCOME_TEXT.format(name=message.from_user.first_name),
            reply_markup=main_reply_keyboard(),
            parse_mode="HTML"
        )

    await message.answer("👇 Menyudan tanlang:", reply_markup=main_menu())


@router.message(F.text == "/ref")
async def cmd_ref_code(message: Message, state: FSMContext):
    await message.answer(
        "📋 Referal kodingizni kiriting:\n\n"
        "Masalan: <code>REF_123456789</code>",
        parse_mode="HTML"
    )
    await state.set_state(RefCodeState.waiting_code)


@router.message(RefCodeState.waiting_code)
async def process_ref_code(message: Message, state: FSMContext):
    code = message.text.strip().upper().replace("REF_", "")
    try:
        ref_id = int(code)
        if ref_id == message.from_user.id:
            await message.answer("❌ O'z referal kodingizni kirita olmaysiz!")
            await state.clear()
            return
        async with aiosqlite.connect("bot.db") as db:
            async with db.execute("SELECT user_id FROM users WHERE user_id=?", (ref_id,)) as cur:
                exists = await cur.fetchone()
            if not exists:
                await message.answer("❌ Bunday referal kod topilmadi!")
                await state.clear()
                return
            async with db.execute("SELECT referred_by FROM users WHERE user_id=?", (message.from_user.id,)) as cur:
                row = await cur.fetchone()
            if row and row[0]:
                await message.answer("❌ Siz allaqachon referal kod ishlatgansiz!")
                await state.clear()
                return
            await db.execute(
                "UPDATE users SET referred_by=? WHERE user_id=?",
                (ref_id, message.from_user.id)
            )
            await db.commit()
        await state.clear()
        await message.answer(
            "✅ Referal kod qabul qilindi!\n\n"
            "Birinchi buyurtmangizdan so'ng do'stingiz <b>500 so'm bonus</b> oladi.",
            reply_markup=back_to_main(),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            "❌ Noto'g'ri format. Masalan: <code>REF_123456789</code>",
            parse_mode="HTML"
        )


def _referral_text(stats: dict, ref_link: str, user_id: int, bonus: int, percent: float) -> str:
    return (
        "🎁 <b>Referal dasturi</b>\n\n"
        "Do'stlaringizni taklif qiling va ularning har bir buyurtmasidan daromad oling!\n\n"
        "💸 <b>Qanday ishlaydi?</b>\n"
        "├ Do'stingiz havolangiz orqali kiradi\n"
        f"├ Birinchi buyurtma bersa → sizga <b>+{bonus:,} so'm bonus</b>\n"
        f"└ Keyingi har buyurtmasidan → <b>{percent:.0f}% avtomatik balansga</b>\n\n"
        "📊 <b>Sizning statistikangiz:</b>\n"
        f"├ 👥 Taklif qilganlar: <b>{stats['invited']} kishi</b>\n"
        f"├ 🎁 Bonus daromad: <b>{stats['bonus_earned']:,.0f} so'm</b>\n"
        f"├ 💰 Foiz daromad: <b>{stats['percent_earned']:,.0f} so'm</b>\n"
        f"└ 📈 Jami daromad: <b>{stats['total_earned']:,.0f} so'm</b>\n\n"
        "🔗 <b>Sizning havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        "💡 Chegara yo'q — qancha ko'p odam, shuncha ko'p daromad! 🚀"
    )


@router.message(F.text.in_(REPLY_TO_CALLBACK.keys()))
async def handle_reply_button(message: Message):
    callback_data = REPLY_TO_CALLBACK[message.text]

    if callback_data == "balance":
        from keyboards.menus import balance_menu
        bal = await get_balance(message.from_user.id)
        await message.answer(
            f"💰 <b>Balansingiz:</b> {bal:,.0f} so'm\n\n"
            "Balansni to'ldirish uchun quyidagi tugmani bosing.",
            reply_markup=balance_menu(),
            parse_mode="HTML"
        )

    elif callback_data == "services":
        await message.answer(
            "🛍 <b>Hizmatlar</b>\n\nPlatformani tanlang:",
            reply_markup=services_menu(),
            parse_mode="HTML"
        )

    elif callback_data == "my_orders":
        orders = await get_user_orders(message.from_user.id)
        if not orders:
            await message.answer(
                "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
                reply_markup=back_to_main(),
                parse_mode="HTML"
            )
            return
        STATUS_EMOJI = {
            "Pending": "⏳", "In progress": "🔄", "Processing": "🔄",
            "Completed": "✅", "Partial": "⚠️", "Canceled": "❌", "Refunded": "💸"
        }
        lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
        for o in orders:
            emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
            lines.append(
                f"{emoji} <b>#{o.get('smm_order_id')}</b> | {o.get('service_name','')[:28]}\n"
                f"   🔢 {o.get('quantity',0):,} | 💰 {o.get('price_uzs',0):,.0f} so'm | {o.get('status')}\n"
            )
        await message.answer("\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML")

    elif callback_data == "support":
        admin_username = os.getenv("ADMIN_USERNAME", "your_admin_username")
        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(text="👨‍💼 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}"))
        b.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
        await message.answer(
            "🆘 <b>Yordam</b>\n\n"
            "Savol yoki muammolaringiz bo'lsa admin bilan bog'laning 👇\n\n"
            "❓ <b>Buyurtma qancha vaqtda bajariladi?</b>\n"
            "➡️ 1 daqiqadan bir necha soatgacha\n\n"
            "❓ <b>Balans qanday to'ldiriladi?</b>\n"
            "➡️ Kartaga o'tkazma, chek 5 daqiqada tasdiqlanadi\n\n"
            "❓ <b>Buyurtma bajarilmasa pul qaytadimi?</b>\n"
            "➡️ Ha, bajarilmagan qismi qaytariladi\n\n"
            "❓ <b>Minimal to'ldirish summasi?</b>\n"
            "➡️ 5,000 so'mdan boshlanadi",
            reply_markup=b.as_markup(),
            parse_mode="HTML"
        )

    elif callback_data == "referral":
        from database import get_referral_stats
        from config import REFERRAL_PERCENT, REFERRAL_BONUS
        user_id = message.from_user.id
        stats = await get_referral_stats(user_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{user_id}"
        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(
            text="🔗 Havolani ulashish",
            switch_inline_query=(
                f"🚀 Telegram va Instagram uchun eng arzon SMM xizmatlari!\n\n"
                f"✅ Minglab mijozlar ishongan panel\n"
                f"💰 Narxlar bozordan 5x arzon\n"
                f"⚡ Buyurtma bir zumda bajariladi\n"
                f"🎁 Ro'yxatdan o'tsangiz bonus kutmoqda!\n\n"
                f"👇 Hoziroq sinab ko'ring:\n"
                f"https://t.me/{BOT_USERNAME}?start=REF_{user_id}"
            )
        ))
        b.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
        await message.answer(
            _referral_text(stats, ref_link, user_id, REFERRAL_BONUS, REFERRAL_PERCENT),
            reply_markup=b.as_markup(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        WELCOME_TEXT.format(name=call.from_user.first_name),
        reply_markup=main_menu(),
        parse_mode="HTML"
    )
    await call.answer()