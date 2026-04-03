import os
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import (
    get_or_create_user, get_balance, get_user_orders,
    get_referral_stats, get_referral_history, get_referral_history_count,
    add_referral_earning
)
from config import REFERRAL_PERCENT, REFERRAL_BONUS

router = Router()

BOT_USERNAME = os.getenv("BOT_USERNAME", "zendor_smm_bot")
SIGNUP_BONUS = int(os.getenv("SIGNUP_BONUS", "100"))   # Ro'yxatdan o'tganda
DEPOSIT_BONUS = int(os.getenv("DEPOSIT_BONUS", "500"))  # Balans to'ldirganda

ADMIN_IDS_RAW = os.getenv("ADMIN_ID", "7917217047")
try:
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]
except Exception:
    ADMIN_IDS = [int(ADMIN_IDS_RAW)]

USER_COMMANDS = [
    ("start",       "🚀 Botni ishga tushirish"),
    ("commandlist", "📋 Barcha komandalar"),
    ("balans",      "💰 Balansni ko'rish"),
    ("xizmatlar",   "📦 Xizmatlar"),
    ("buyurtmalar", "🗂 Buyurtmalarim"),
    ("referral",    "🎁 Referal dasturi"),
    ("yordam",      "🆘 Yordam"),
]

ADMIN_COMMANDS = [
    ("admin",         "🛠 Admin panel"),
    ("stats",         "📊 Statistika"),
    ("users",         "👥 Foydalanuvchilar"),
    ("pending",       "⏳ Kutayotgan depozitlar"),
    ("top",           "🏆 Top 10 mijozlar"),
    ("balance_check", "💳 Balans tekshirish <id>"),
    ("add_balance",   "➕ Balans qo'shish <id> <summa>"),
    ("discount",      "🏷 Chegirma o'rnatish <id> <foiz>"),
    ("broadcast",     "📢 Hammaga xabar"),
]

WELCOME_TEXT = (
    "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
    "🚀 <b>Zendor SMM</b> — Telegram, Instagram, TikTok,\n"
    "YouTube va Facebook uchun eng arzon SMM!\n\n"
    "⚡ <b>Nima qila olasiz?</b>\n"
    "├ 📈 Obunachi, ko'rish, layk oshirish\n"
    "├ 💰 Balansni karta orqali to'ldirish\n"
    "└ 🎁 Do'stlarni taklif qilib pul ishlash\n\n"
    "👇 Menyudan tanlang:"
)

REPLY_MAP = {
    "📦 Xizmatlar":     "services",
    "💰 Balans":        "balance",
    "🗂 Buyurtmalarim": "my_orders",
    "ℹ️ Yordam":        "support",
    "🎁 Referal":       "referral",
}

STATUS_EMOJI = {
    "Pending":     "⏳",
    "In progress": "🔄",
    "In Progress": "🔄",
    "Processing":  "🔄",
    "Completed":   "✅",
    "Partial":     "⚠️",
    "Canceled":    "❌",
    "Cancelled":   "❌",
    "Refunded":    "💸",
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
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 Xizmatlar", callback_data="services"),
        InlineKeyboardButton(text="💰 Balans", callback_data="balance")
    )
    builder.row(
        InlineKeyboardButton(text="🗂 Buyurtmalarim", callback_data="my_orders"),
        InlineKeyboardButton(text="ℹ️ Yordam", callback_data="support")
    )
    builder.row(InlineKeyboardButton(text="🎁 Referal dasturi", callback_data="referral"))
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
    from smm_api import get_platform_names
    builder = InlineKeyboardBuilder()
    names = get_platform_names()
    for i in range(0, len(names), 2):
        row = names[i:i+2]
        builder.row(*[InlineKeyboardButton(text=n, callback_data=f"plat_{n}") for n in row])
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    return builder.as_markup()


def referral_keyboard(user_id: int):
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{user_id}"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🔗 Havolani ulashish",
        switch_inline_query=(
            f"🚀 Telegram, Instagram, TikTok, YouTube uchun eng arzon SMM!\n\n"
            f"✅ Ishonchli | ⚡ Tez | 💰 Arzon\n\n"
            f"👇 Ro'yxatdan o'ting:\n{ref_link}"
        )
    ))
    builder.row(InlineKeyboardButton(
        text="📋 Referal tarixim",
        callback_data="referral_history_0"
    ))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()


def _referral_text(stats: dict, ref_link: str) -> str:
    return (
        "🎁 <b>Referal dasturi</b>\n\n"
        "Do'stlaringizni taklif qiling va avtomatik daromad oling!\n\n"
        "💸 <b>Qanday ishlaydi?</b>\n"
        f"├ Ro'yxatdan o'tsa → <b>+{SIGNUP_BONUS:,} so'm</b> (darhol)\n"
        f"├ Balans to'ldirsa → <b>+{DEPOSIT_BONUS:,} so'm</b>\n"
        f"└ Har buyurtmasidan → <b>{REFERRAL_PERCENT:.0f}% avtomatik</b>\n\n"
        "📊 <b>Sizning statistikangiz:</b>\n"
        f"├ 👥 Taklif qilganlar: <b>{stats['invited']} kishi</b>\n"
        f"├ 🎁 Bonus daromad: <b>{stats['bonus_earned']:,.0f} so'm</b>\n"
        f"├ 💰 Foiz daromad: <b>{stats['percent_earned']:,.0f} so'm</b>\n"
        f"└ 📈 Jami daromad: <b>{stats['total_earned']:,.0f} so'm</b>\n\n"
        "🔗 <b>Sizning havolangiz:</b>\n"
        f"<code>{ref_link}</code>"
    )


# ── /start ────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    args = message.text.split()
    referred_by = None

    if len(args) > 1 and args[1].startswith("REF_"):
        try:
            ref_id = int(args[1].replace("REF_", ""))
            if ref_id != message.from_user.id:
                referred_by = ref_id
        except ValueError:
            pass

    is_new = await get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
        referred_by=referred_by
    )
    await state.clear()

    # Yangi foydalanuvchi referal orqali kelsa:
    # - Unga hech qanday maxsus xabar yo'q (oddiy welcome)
    # - Referal egasiga: "kimdir kirdi + 100 so'm tushdi"
    if is_new and referred_by:
        user = message.from_user
        name = f"@{user.username}" if user.username else user.full_name
        try:
            await add_referral_earning(
                referred_by, user.id, SIGNUP_BONUS, 0, "signup_bonus"
            )
            await bot.send_message(
                referred_by,
                f"👤 <b>Yangi referal!</b>\n\n"
                f"{name} sizning havolangiz orqali ro'yxatdan o'tdi!\n"
                f"➕ <b>+{SIGNUP_BONUS:,} so'm</b> balansingizga tushdi!",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await message.answer(
        WELCOME_TEXT.format(name=message.from_user.first_name),
        reply_markup=main_reply_keyboard(),
        parse_mode="HTML"
    )
    await message.answer(
        "⬇️ Quyidagi menyudan tanlang:",
        reply_markup=main_menu_keyboard()
    )


# ── Komandalar ────────────────────────────────────────────────

@router.message(Command("commandlist", "commandList", "commands"))
async def cmd_commandlist(message: Message):
    is_adm = message.from_user.id in ADMIN_IDS
    lines = ["👤 <b>Foydalanuvchi komandalar:</b>\n"]
    for cmd, desc in USER_COMMANDS:
        lines.append(f"/{cmd} — {desc}")
    if is_adm:
        lines.append("\n\n🛠 <b>Admin komandalar:</b>\n")
        for cmd, desc in ADMIN_COMMANDS:
            lines.append(f"/{cmd} — {desc}")
    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=back_to_main())


@router.message(Command("balans", "balance"))
async def cmd_balans(message: Message):
    bal = await get_balance(message.from_user.id)
    await message.answer(
        f"💰 <b>Balansingiz:</b> {bal:,} so'm",
        reply_markup=balance_menu(), parse_mode="HTML"
    )


@router.message(Command("xizmatlar", "services"))
async def cmd_xizmatlar(message: Message):
    await message.answer(
        "🛍 <b>Xizmatlar</b>\n\nPlatformani tanlang:",
        reply_markup=services_menu(), parse_mode="HTML"
    )


@router.message(Command("buyurtmalar"))
async def cmd_buyurtmalar(message: Message):
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer(
            "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
            reply_markup=back_to_main(), parse_mode="HTML"
        )
        return
    lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20):\n"]
    for o in orders:
        emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
        lines.append(
            f"{emoji} <b>#{o.get('smm_order_id')}</b> | "
            f"{(o.get('service_name') or '')[:28]}\n"
            f"   🔢 {o.get('quantity', 0):,} | 💰 {o.get('price_uzs', 0):,.0f} so'm\n"
        )
    await message.answer("\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML")


@router.message(Command("referral"))
async def cmd_referral(message: Message):
    stats = await get_referral_stats(message.from_user.id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{message.from_user.id}"
    await message.answer(
        _referral_text(stats, ref_link),
        reply_markup=referral_keyboard(message.from_user.id),
        parse_mode="HTML"
    )


@router.message(Command("yordam"))
async def cmd_yordam(message: Message):
    admin_username = os.getenv("ADMIN_USERNAME", "smo_2811").lstrip("@")
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👨‍💼 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}"
    ))
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
        "➡️ 5,000 so'mdan boshlanadi",
        reply_markup=builder.as_markup(), parse_mode="HTML"
    )


# ── Reply tugmalar ────────────────────────────────────────────

@router.message(F.text.in_(REPLY_MAP.keys()))
async def handle_reply_button(message: Message):
    cb = REPLY_MAP[message.text]

    if cb == "balance":
        bal = await get_balance(message.from_user.id)
        await message.answer(
            f"💰 <b>Balansingiz:</b> {bal:,} so'm",
            reply_markup=balance_menu(), parse_mode="HTML"
        )

    elif cb == "services":
        await message.answer(
            "🛍 <b>Xizmatlar</b>\n\nPlatformani tanlang:",
            reply_markup=services_menu(), parse_mode="HTML"
        )

    elif cb == "my_orders":
        orders = await get_user_orders(message.from_user.id)
        if not orders:
            await message.answer(
                "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
                reply_markup=back_to_main(), parse_mode="HTML"
            )
            return
        lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20):\n"]
        for o in orders:
            emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
            lines.append(
                f"{emoji} <b>#{o.get('smm_order_id')}</b> | "
                f"{(o.get('service_name') or '')[:28]}\n"
                f"   🔢 {o.get('quantity', 0):,} | 💰 {o.get('price_uzs', 0):,.0f} so'm\n"
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
        stats = await get_referral_stats(message.from_user.id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{message.from_user.id}"
        await message.answer(
            _referral_text(stats, ref_link),
            reply_markup=referral_keyboard(message.from_user.id),
            parse_mode="HTML"
        )


# ── Callback handlerlari ──────────────────────────────────────

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        WELCOME_TEXT.format(name=call.from_user.first_name),
        reply_markup=main_menu_keyboard(), parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "balance")
async def cb_balance(call: CallbackQuery):
    bal = await get_balance(call.from_user.id)
    await call.message.edit_text(
        f"💰 <b>Balansingiz:</b> {bal:,} so'm\n\nBalansni to'ldirish uchun bosing.",
        reply_markup=balance_menu(), parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "my_orders")
async def cb_orders(call: CallbackQuery):
    orders = await get_user_orders(call.from_user.id)
    if not orders:
        await call.message.edit_text(
            "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
            reply_markup=back_to_main(), parse_mode="HTML"
        )
        await call.answer()
        return
    lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20):\n"]
    for o in orders:
        emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
        lines.append(
            f"{emoji} <b>#{o.get('smm_order_id')}</b> | "
            f"{(o.get('service_name') or '')[:28]}\n"
            f"   🔢 {o.get('quantity', 0):,} | 💰 {o.get('price_uzs', 0):,.0f} so'm\n"
        )
    await call.message.edit_text(
        "\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "support")
async def cb_support(call: CallbackQuery):
    admin_username = os.getenv("ADMIN_USERNAME", "smo_2811").lstrip("@")
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👨‍💼 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}"
    ))
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
        reply_markup=builder.as_markup(), parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "referral")
async def cb_referral(call: CallbackQuery):
    stats = await get_referral_stats(call.from_user.id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{call.from_user.id}"
    await call.message.edit_text(
        _referral_text(stats, ref_link),
        reply_markup=referral_keyboard(call.from_user.id),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("referral_history_"))
async def cb_referral_history(call: CallbackQuery):
    import time as _time
    page = int(call.data.split("_")[2])
    PAGE_SIZE = 5

    rows = await get_referral_history(call.from_user.id, limit=PAGE_SIZE, offset=page * PAGE_SIZE)
    total = await get_referral_history_count(call.from_user.id)

    builder = InlineKeyboardBuilder()

    if not rows:
        builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="referral"))
        await call.message.edit_text(
            "📋 <b>Referal tarixi</b>\n\nHali referal daromad yo'q.",
            reply_markup=builder.as_markup(), parse_mode="HTML"
        )
        await call.answer()
        return

    start = page * PAGE_SIZE + 1
    end = page * PAGE_SIZE + len(rows)
    lines = [f"📋 <b>Referal tarixi</b> ({start}–{end} / {total})\n"]

    TYPE_ICON = {
        "signup_bonus":  "👤",
        "deposit_bonus": "💳",
        "percent":       "💰",
    }
    TYPE_LABEL = {
        "signup_bonus":  "Ro'yxatdan o'tdi",
        "deposit_bonus": "Balans to'ldirdi",
        "percent":       "Buyurtma berdi",
    }

    for r in rows:
        icon = TYPE_ICON.get(r["type"], "💸")
        label = TYPE_LABEL.get(r["type"], r["type"])
        from_name = r.get("from_name") or f"ID:{r['from_user']}"
        ts = _time.strftime("%d.%m.%Y", _time.localtime(r.get("created_at", 0)))
        lines.append(
            f"{icon} <b>+{r['amount']:,} so'm</b> — {from_name}\n"
            f"   {label} | {ts}"
        )

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="⬅️ Oldingi", callback_data=f"referral_history_{page - 1}"
        ))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(InlineKeyboardButton(
            text="Keyingi ➡️", callback_data=f"referral_history_{page + 1}"
        ))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="referral"))

    await call.message.edit_text(
        "\n".join(lines), reply_markup=builder.as_markup(), parse_mode="HTML"
    )
    await call.answer()