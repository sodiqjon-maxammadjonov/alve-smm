import os
import time
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import get_or_create_user, get_balance, get_user_orders

router = Router()

BOT_USERNAME = os.getenv("BOT_USERNAME", "zendor_smm_bot")
ADMIN_IDS_RAW = os.getenv("ADMIN_ID", "7917217047")
try:
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]
except Exception:
    ADMIN_IDS = [int(ADMIN_IDS_RAW)]

# ── Komandalar ro'yxati ───────────────────────────────────────

USER_COMMANDS = [
    ("start",        "🚀 Botni ishga tushirish"),
    ("commandlist",  "📋 Barcha komandalar ro'yxati"),
    ("balans",       "💰 Balansni ko'rish"),
    ("xizmatlar",    "📦 Xizmatlar ro'yxati"),
    ("buyurtmalar",  "🗂 Buyurtmalarim"),
    ("referral",     "🎁 Referal dasturi"),
    ("yordam",       "🆘 Yordam va FAQ"),
]

ADMIN_COMMANDS = [
    ("admin",          "🛠  Admin panel (tugmali)"),
    ("stats",          "📊 Bot statistikasi"),
    ("users",          "👥 Foydalanuvchilar"),
    ("pending",        "⏳ Kutayotgan depozitlar"),
    ("top",            "🏆 Top 10 mijozlar"),
    ("balance_check",  "💳 Foydalanuvchi balansi  <id>"),
    ("add_balance",    "➕ Balans qo'shish  <id> <summa>"),
    ("broadcast",      "📢 Hammaga xabar yuborish"),
    ("commandlist",    "📋 Komandalar ro'yxati"),
]

WELCOME_TEXT = (
    "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
    "🚀 <b>Zendor SMM</b> — Telegram va Instagram uchun\n"
    "eng arzon va tez SMM xizmatlari!\n\n"
    "⚡ <b>Nima qila olasiz?</b>\n"
    "├ 📈 Kanal/sahifa obunachilari oshirish\n"
    "├ 👁 Post ko'rishlarini oshirish\n"
    "├ ❤️ Layk va reaksiyalar qo'shish\n"
    "└ 🎁 Do'stlarni taklif qilib pul ishlash\n\n"
    "👇 Quyidagi menyudan boshlang:"
)

REPLY_TO_CALLBACK = {
    "📦 Xizmatlar":     "services",
    "💰 Balans":        "balance",
    "🗂 Buyurtmalarim": "my_orders",
    "ℹ️ Yordam":        "support",
    "🎁 Referal":       "referral",
}


# ── Klaviaturalar ─────────────────────────────────────────────

def main_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📦 Xizmatlar"),
        KeyboardButton(text="💰 Balans")
    )
    builder.row(
        KeyboardButton(text="🗂 Buyurtmalarim"),
        KeyboardButton(text="ℹ️ Yordam")
    )
    builder.row(KeyboardButton(text="🎁 Referal"))
    return builder.as_markup(resize_keyboard=True)


def main_menu_keyboard():
    """Zamonaviy inline menyu — Bot API 9.4 button style bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📦 Xizmatlar",
            callback_data="services"
        ),
        InlineKeyboardButton(
            text="💰 Balans",
            callback_data="balance"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🗂 Buyurtmalarim",
            callback_data="my_orders"
        ),
        InlineKeyboardButton(
            text="ℹ️ Yordam",
            callback_data="support"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🎁 Referal dasturi",
            callback_data="referral"
        )
    )
    return builder.as_markup()


def back_to_main():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()


def balance_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Balansni to'ldirish", callback_data="deposit"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    return builder.as_markup()


def services_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✈️ Telegram", callback_data="platform_telegram"))
    builder.row(InlineKeyboardButton(text="📸 Instagram", callback_data="platform_instagram"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    return builder.as_markup()


# ── /commandList ──────────────────────────────────────────────

@router.message(Command("commandlist", "commandList", "commands"))
async def cmd_commandlist(message: Message):
    user_id = message.from_user.id
    is_adm = user_id in ADMIN_IDS

    # Foydalanuvchi komandalar
    user_lines = ["👤 <b>Foydalanuvchi komandalar:</b>\n"]
    for cmd, desc in USER_COMMANDS:
        user_lines.append(f"/{cmd} — {desc}")

    if is_adm:
        admin_lines = ["\n\n🛠 <b>Admin komandalar:</b>\n"]
        for cmd, desc in ADMIN_COMMANDS:
            admin_lines.append(f"/{cmd} — {desc}")
        text = "\n".join(user_lines) + "\n".join(admin_lines)
    else:
        text = "\n".join(user_lines)

    await message.answer(text, parse_mode="HTML", reply_markup=back_to_main())


# ── /start ────────────────────────────────────────────────────

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
            "🎉 <b>Siz do'stingiz taklifi orqali keldingiz!</b>\n\n"
            "Birinchi buyurtmangizdan so'ng do'stingiz bonus oladi.\n\n"
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

    await message.answer(
        "⬇️ Quyidagi menyudan tanlang:",
        reply_markup=main_menu_keyboard()
    )


# ── Komanda handlerlari ───────────────────────────────────────

@router.message(Command("balans", "balance"))
async def cmd_balans(message: Message):
    bal = await get_balance(message.from_user.id)
    await message.answer(
        f"💰 <b>Balansingiz:</b> {bal:,} so'm\n\n"
        "Balansni to'ldirish uchun quyidagi tugmani bosing.",
        reply_markup=balance_menu(),
        parse_mode="HTML"
    )


@router.message(Command("xizmatlar", "services"))
async def cmd_xizmatlar(message: Message):
    await message.answer(
        "🛍 <b>Xizmatlar</b>\n\nPlatformani tanlang:",
        reply_markup=services_menu(),
        parse_mode="HTML"
    )


@router.message(Command("buyurtmalar", "orders"))
async def cmd_buyurtmalar(message: Message):
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
            f"   🔢 {o.get('quantity',0):,} | 💰 {o.get('price_uzs',0):,.0f} so'm\n"
        )
    await message.answer("\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML")


@router.message(Command("yordam", "help"))
async def cmd_yordam(message: Message):
    admin_username = os.getenv("ADMIN_USERNAME", "smo_2811").lstrip("@")
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👨‍💼 Admin bilan bog'lanish",
        url=f"https://t.me/{admin_username}"
    ))
    builder.row(InlineKeyboardButton(text="📋 Komandalar", callback_data="commandlist_cb"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    await message.answer(
        "🆘 <b>Yordam</b>\n\n"
        "❓ <b>Buyurtma qancha vaqtda bajariladi?</b>\n"
        "➡️ 1 daqiqadan bir necha soatgacha\n\n"
        "❓ <b>Balans qanday to'ldiriladi?</b>\n"
        "➡️ Kartaga o'tkazma, chek 5 daqiqada tasdiqlanadi\n\n"
        "❓ <b>Buyurtma bajarilmasa pul qaytadimi?</b>\n"
        "➡️ Ha, bajarilmagan qismi qaytariladi\n\n"
        "❓ <b>Minimal to'ldirish summasi?</b>\n"
        "➡️ 5,000 so'mdan boshlanadi\n\n"
        "❓ <b>Komandalar ro'yxati?</b>\n"
        "➡️ /commandlist",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.message(Command("referral"))
async def cmd_referral_msg(message: Message):
    from database import get_referral_stats
    from config import REFERRAL_PERCENT, REFERRAL_BONUS
    stats = await get_referral_stats(message.from_user.id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{message.from_user.id}"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🔗 Havolani ulashish",
        switch_inline_query=(
            f"🚀 Telegram va Instagram uchun eng arzon SMM!\n\n"
            f"✅ Ishonchli panel | ⚡ Tez yetkazish\n"
            f"💰 Bozordan 5x arzon narxlar\n\n"
            f"👇 Ro'yxatdan o'ting:\n{ref_link}"
        )
    ))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    await message.answer(
        _referral_text(stats, ref_link, REFERRAL_BONUS, REFERRAL_PERCENT),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


# ── Reply tugmalar ────────────────────────────────────────────

@router.message(F.text.in_(REPLY_TO_CALLBACK.keys()))
async def handle_reply_button(message: Message):
    cb = REPLY_TO_CALLBACK[message.text]
    if cb == "balance":
        bal = await get_balance(message.from_user.id)
        await message.answer(
            f"💰 <b>Balansingiz:</b> {bal:,} so'm\n\nBalansni to'ldirish uchun bosing.",
            reply_markup=balance_menu(),
            parse_mode="HTML"
        )
    elif cb == "services":
        await message.answer(
            "🛍 <b>Xizmatlar</b>\n\nPlatformani tanlang:",
            reply_markup=services_menu(),
            parse_mode="HTML"
        )
    elif cb == "my_orders":
        orders = await get_user_orders(message.from_user.id)
        STATUS_EMOJI = {
            "Pending": "⏳", "In progress": "🔄", "Processing": "🔄",
            "Completed": "✅", "Partial": "⚠️", "Canceled": "❌", "Refunded": "💸"
        }
        if not orders:
            await message.answer(
                "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
                reply_markup=back_to_main(), parse_mode="HTML"
            )
            return
        lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
        for o in orders:
            emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
            lines.append(
                f"{emoji} <b>#{o.get('smm_order_id')}</b> | {o.get('service_name','')[:28]}\n"
                f"   🔢 {o.get('quantity',0):,} | 💰 {o.get('price_uzs',0):,.0f} so'm\n"
            )
        await message.answer("\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML")
    elif cb == "support":
        admin_username = os.getenv("ADMIN_USERNAME", "smo_2811").lstrip("@")
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="👨‍💼 Admin", url=f"https://t.me/{admin_username}"
        ))
        builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
        await message.answer(
            "🆘 <b>Yordam kerakmi?</b>\n\nAdmin bilan bog'laning 👇",
            reply_markup=builder.as_markup(), parse_mode="HTML"
        )
    elif cb == "referral":
        from database import get_referral_stats
        from config import REFERRAL_PERCENT, REFERRAL_BONUS
        stats = await get_referral_stats(message.from_user.id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{message.from_user.id}"
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="🔗 Havolani ulashish",
            switch_inline_query=(
                f"🚀 Eng arzon SMM xizmatlari!\n{ref_link}"
            )
        ))
        builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
        await message.answer(
            _referral_text(stats, ref_link, REFERRAL_BONUS, REFERRAL_PERCENT),
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )


# ── Callback handlerlari ──────────────────────────────────────

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        WELCOME_TEXT.format(name=call.from_user.first_name),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "balance")
async def cb_balance(call: CallbackQuery):
    bal = await get_balance(call.from_user.id)
    await call.message.edit_text(
        f"💰 <b>Balansingiz:</b> {bal:,} so'm\n\nBalansni to'ldirish uchun bosing.",
        reply_markup=balance_menu(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "my_orders")
async def cb_orders(call: CallbackQuery):
    orders = await get_user_orders(call.from_user.id)
    STATUS_EMOJI = {
        "Pending": "⏳", "In progress": "🔄", "Processing": "🔄",
        "Completed": "✅", "Partial": "⚠️", "Canceled": "❌", "Refunded": "💸"
    }
    if not orders:
        await call.message.edit_text(
            "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
            reply_markup=back_to_main(), parse_mode="HTML"
        )
        await call.answer()
        return
    lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
    for o in orders:
        emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
        lines.append(
            f"{emoji} <b>#{o.get('smm_order_id')}</b> | {o.get('service_name','')[:28]}\n"
            f"   🔢 {o.get('quantity',0):,} | 💰 {o.get('price_uzs',0):,.0f} so'm\n"
        )
    await call.message.edit_text("\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "support")
async def cb_support(call: CallbackQuery):
    admin_username = os.getenv("ADMIN_USERNAME", "smo_2811").lstrip("@")
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👨‍💼 Admin bilan bog'lanish",
        url=f"https://t.me/{admin_username}"
    ))
    builder.row(InlineKeyboardButton(text="📋 Komandalar", callback_data="commandlist_cb"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    await call.message.edit_text(
        "🆘 <b>Yordam</b>\n\n"
        "❓ <b>Buyurtma qancha vaqtda bajariladi?</b>\n"
        "➡️ 1 daqiqadan bir necha soatgacha\n\n"
        "❓ <b>Balans qanday to'ldiriladi?</b>\n"
        "➡️ Kartaga o'tkazma, chek 5 daqiqada tasdiqlanadi\n\n"
        "❓ <b>Buyurtma bajarilmasa pul qaytadimi?</b>\n"
        "➡️ Ha, bajarilmagan qismi qaytariladi\n\n"
        "❓ <b>Minimal to'ldirish summasi?</b>\n"
        "➡️ 5,000 so'mdan boshlanadi",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "referral")
async def cb_referral(call: CallbackQuery):
    from database import get_referral_stats
    from config import REFERRAL_PERCENT, REFERRAL_BONUS
    stats = await get_referral_stats(call.from_user.id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{call.from_user.id}"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🔗 Havolani ulashish",
        switch_inline_query=(
            f"🚀 Telegram va Instagram uchun eng arzon SMM!\n\n"
            f"✅ Ishonchli panel | ⚡ Tez yetkazish\n"
            f"💰 Bozordan 5x arzon narxlar\n\n"
            f"👇 Ro'yxatdan o'ting:\n{ref_link}"
        )
    ))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    await call.message.edit_text(
        _referral_text(stats, ref_link, REFERRAL_BONUS, REFERRAL_PERCENT),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "commandlist_cb")
async def cb_commandlist(call: CallbackQuery):
    is_adm = call.from_user.id in ADMIN_IDS
    user_lines = ["👤 <b>Foydalanuvchi komandalar:</b>\n"]
    for cmd, desc in USER_COMMANDS:
        user_lines.append(f"/{cmd} — {desc}")

    if is_adm:
        admin_lines = ["\n\n🛠 <b>Admin komandalar:</b>\n"]
        for cmd, desc in ADMIN_COMMANDS:
            admin_lines.append(f"/{cmd} — {desc}")
        text = "\n".join(user_lines) + "\n".join(admin_lines)
    else:
        text = "\n".join(user_lines)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
    await call.answer()


# ── Yordamchi funksiya ────────────────────────────────────────

def _referral_text(stats: dict, ref_link: str, bonus: int, percent: float) -> str:
    return (
        "🎁 <b>Referal dasturi</b>\n\n"
        "Do'stlaringizni taklif qiling va daromad oling!\n\n"
        "💸 <b>Qanday ishlaydi?</b>\n"
        f"├ Do'st birinchi buyurtma bersa → <b>+{bonus:,} so'm bonus</b>\n"
        f"└ Har keyingi buyurtmasidan → <b>{percent:.0f}% avtomatik</b>\n\n"
        "📊 <b>Sizning statistikangiz:</b>\n"
        f"├ 👥 Taklif qilganlar: <b>{stats['invited']} kishi</b>\n"
        f"├ 🎁 Bonus: <b>{stats['bonus_earned']:,.0f} so'm</b>\n"
        f"├ 💰 Foiz: <b>{stats['percent_earned']:,.0f} so'm</b>\n"
        f"└ 📈 Jami: <b>{stats['total_earned']:,.0f} so'm</b>\n\n"
        "🔗 <b>Sizning havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        "💡 Chegara yo'q — qancha ko'p odam, shuncha ko'p daromad! 🚀"
    )