"""
start.py — Zendor SMM Bot
Bosh menyu, xush kelibsiz, balans, buyurtmalar, referal, yordam.
2026 yangi dizayn.
"""

import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import (
    get_or_create_user, get_balance, get_user_orders,
    get_referral_stats, get_referral_history,
    get_referral_history_count, add_referral_earning,
)
from keyboards.menus import (
    main_reply_keyboard, main_menu_keyboard,
    balance_menu, back_to_main, referral_keyboard,
    referral_history_keyboard, support_keyboard,
)
from config import REFERRAL_PERCENT, REFERRAL_BONUS

router = Router()

BOT_USERNAME  = os.getenv("BOT_USERNAME", "zendor_smm_bot")
SIGNUP_BONUS  = int(os.getenv("SIGNUP_BONUS",  "100"))
DEPOSIT_BONUS = int(os.getenv("DEPOSIT_BONUS", "500"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")

ADMIN_IDS_RAW = os.getenv("ADMIN_ID", "7917217047")
try:
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]
except Exception:
    ADMIN_IDS = [int(ADMIN_IDS_RAW)]

# Reply tugmalar → callback map
REPLY_MAP = {
    "🛍 Xizmatlar":     "services",
    "💰 Balans":         "balance",
    "📋 Buyurtmalarim": "my_orders",
    "🎁 Referal":        "referral",
    "🆘 Yordam":         "support",
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

# ── Matnlar ───────────────────────────────────────────────────

def welcome_text(name: str) -> str:
    return (
        f"👋 Assalomu alaykum, <b>{name}</b>!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <b>Zendor SMM</b> — O'zbekistondagi\n"
        "eng zamonaviy SMM paneli!\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌐 <b>Platformalar:</b>\n"
        "├ ✈️ Telegram  📸 Instagram\n"
        "├ 🎵 TikTok   ▶️ YouTube\n"
        "└ 📘 Facebook  🐦 Twitter/X\n\n"
        "💡 <b>Imkoniyatlar:</b>\n"
        "├ 📈 Obunachi, ko'rish, layk, reaksiya\n"
        "├ 💰 Karta orqali balans to'ldirish\n"
        "└ 🎁 Referal dasturi — passiv daromad\n\n"
        "👇 <b>Quyidan tanlang:</b>"
    )


def referral_text(stats: dict, ref_link: str) -> str:
    return (
        "🎁 <b>Referal dasturi</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Do'stlaringizni taklif qiling va\n"
        "<b>avtomatik daromad</b> oling!\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💸 <b>Qanday ishlaydi?</b>\n"
        f"├ 👤 Ro'yxatdan o'tsa → <b>+{SIGNUP_BONUS:,} so'm</b>\n"
        f"├ 💳 Balans to'ldirsa → <b>+{DEPOSIT_BONUS:,} so'm</b>\n"
        f"└ 📦 Buyurtma bersa → <b>{REFERRAL_PERCENT:.0f}% avtomatik</b>\n\n"
        "📊 <b>Sizning statistikangiz:</b>\n"
        f"├ 👥 Taklif qilganlar: <b>{stats['invited']} kishi</b>\n"
        f"├ 🎁 Bonus daromad:   <b>{stats['bonus_earned']:,.0f} so'm</b>\n"
        f"├ 💰 Foiz daromad:    <b>{stats['percent_earned']:,.0f} so'm</b>\n"
        f"└ 📈 Jami daromad:    <b>{stats['total_earned']:,.0f} so'm</b>\n\n"
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
        referred_by=referred_by,
    )
    await state.clear()

    if is_new and referred_by:
        user = message.from_user
        name = f"@{user.username}" if user.username else user.full_name
        try:
            await add_referral_earning(referred_by, user.id, SIGNUP_BONUS, 0, "signup_bonus")
            await bot.send_message(
                referred_by,
                f"🎉 <b>Yangi referal!</b>\n\n"
                f"<b>{name}</b> sizning havolangiz orqali\n"
                f"ro'yxatdan o'tdi!\n\n"
                f"➕ <b>+{SIGNUP_BONUS:,} so'm</b> balansingizga tushdi!",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await message.answer(
        welcome_text(message.from_user.first_name),
        reply_markup=main_reply_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(
        "⬇️ <b>Menyu:</b>",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


# ── /commandlist ──────────────────────────────────────────────

USER_COMMANDS = [
    ("/start",       "🚀 Botni ishga tushirish"),
    ("/commandlist", "📋 Barcha komandalar"),
    ("/balans",      "💰 Balansni ko'rish"),
    ("/xizmatlar",   "📦 Xizmatlar ro'yxati"),
    ("/buyurtmalar", "🗂 Buyurtmalarim"),
    ("/referral",    "🎁 Referal dasturi"),
    ("/yordam",      "🆘 Yordam"),
]

ADMIN_COMMANDS = [
    ("/admin",         "🛠 Admin panel"),
    ("/stats",         "📊 Statistika"),
    ("/users",         "👥 Foydalanuvchilar"),
    ("/pending",       "⏳ Kutayotgan depozitlar"),
    ("/top",           "🏆 Top 10 mijozlar"),
    ("/balance_check", "💳 Balans tekshirish"),
    ("/add_balance",   "➕ Balans qo'shish"),
    ("/discount",      "🏷 Chegirma o'rnatish"),
    ("/broadcast",     "📢 Hammaga xabar"),
]


@router.message(Command("commandlist"))
async def cmd_commandlist(message: Message):
    lines = ["📋 <b>Barcha komandalar:</b>\n"]
    for cmd, desc in USER_COMMANDS:
        lines.append(f"<code>{cmd}</code> — {desc}")

    if message.from_user.id in ADMIN_IDS:
        lines.append("\n🛠 <b>Admin komandalar:</b>")
        for cmd, desc in ADMIN_COMMANDS:
            lines.append(f"<code>{cmd}</code> — {desc}")

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=back_to_main())


@router.message(Command("balans"))
async def cmd_balans(message: Message):
    bal = await get_balance(message.from_user.id)
    await message.answer(
        f"💰 <b>Balansingiz:</b> {bal:,} so'm\n\n"
        f"Balans to'ldirish uchun quyidagi tugmani bosing.",
        reply_markup=balance_menu(),
        parse_mode="HTML",
    )


@router.message(Command("xizmatlar"))
async def cmd_xizmatlar(message: Message):
    from smm_api import get_platform_names
    from keyboards.menus import platforms_keyboard
    await message.answer(
        "🛍 <b>Xizmatlar</b>\n\nPlatformani tanlang:",
        reply_markup=platforms_keyboard(get_platform_names()),
        parse_mode="HTML",
    )


@router.message(Command("buyurtmalar"))
async def cmd_buyurtmalar(message: Message):
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer(
            "📋 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
            reply_markup=back_to_main(), parse_mode="HTML",
        )
        return
    lines = ["📋 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
    for o in orders:
        emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
        lines.append(
            f"{emoji} <b>#{o.get('smm_order_id')}</b>  {(o.get('service_name') or '')[:25]}\n"
            f"   🔢 {o.get('quantity', 0):,}  |  💰 {o.get('price_uzs', 0):,.0f} so'm\n"
        )
    await message.answer("\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML")


@router.message(Command("yordam"))
async def cmd_yordam(message: Message):
    await message.answer(
        _support_text(),
        reply_markup=support_keyboard(ADMIN_USERNAME),
        parse_mode="HTML",
    )


@router.message(Command("referral"))
async def cmd_referral(message: Message):
    stats    = await get_referral_stats(message.from_user.id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{message.from_user.id}"
    await message.answer(
        referral_text(stats, ref_link),
        reply_markup=referral_keyboard(message.from_user.id, BOT_USERNAME),
        parse_mode="HTML",
    )


# ── Reply tugmalar ────────────────────────────────────────────

@router.message(F.text.in_(REPLY_MAP.keys()))
async def handle_reply_button(message: Message):
    cb = REPLY_MAP[message.text]

    if cb == "balance":
        bal = await get_balance(message.from_user.id)
        await message.answer(
            f"💰 <b>Balansingiz</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Joriy balans: <b>{bal:,} so'm</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=balance_menu(),
            parse_mode="HTML",
        )

    elif cb == "services":
        from smm_api import get_platform_names
        from keyboards.menus import platforms_keyboard
        await message.answer(
            "🛍 <b>Xizmatlar</b>\n\nPlatformani tanlang:",
            reply_markup=platforms_keyboard(get_platform_names()),
            parse_mode="HTML",
        )

    elif cb == "my_orders":
        orders = await get_user_orders(message.from_user.id)
        if not orders:
            await message.answer(
                "📋 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
                reply_markup=back_to_main(), parse_mode="HTML",
            )
            return
        lines = ["📋 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
        for o in orders:
            emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
            lines.append(
                f"{emoji} <b>#{o.get('smm_order_id')}</b>  {(o.get('service_name') or '')[:25]}\n"
                f"   🔢 {o.get('quantity', 0):,}  |  💰 {o.get('price_uzs', 0):,.0f} so'm\n"
            )
        await message.answer("\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML")

    elif cb == "support":
        await message.answer(
            _support_text(),
            reply_markup=support_keyboard(ADMIN_USERNAME),
            parse_mode="HTML",
        )

    elif cb == "referral":
        stats    = await get_referral_stats(message.from_user.id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{message.from_user.id}"
        await message.answer(
            referral_text(stats, ref_link),
            reply_markup=referral_keyboard(message.from_user.id, BOT_USERNAME),
            parse_mode="HTML",
        )


# ── Callback handlerlari ──────────────────────────────────────

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        welcome_text(call.from_user.first_name),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "balance")
async def cb_balance(call: CallbackQuery):
    bal = await get_balance(call.from_user.id)
    await call.message.edit_text(
        f"💰 <b>Balansingiz</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Joriy balans: <b>{bal:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Balans to'ldirish uchun quyidagi\n"
        f"tugmani bosing 👇",
        reply_markup=balance_menu(),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "my_orders")
async def cb_orders(call: CallbackQuery):
    orders = await get_user_orders(call.from_user.id)
    if not orders:
        await call.message.edit_text(
            "📋 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.\nXizmatlardan birini tanlang! 👇",
            reply_markup=back_to_main(), parse_mode="HTML",
        )
        await call.answer()
        return

    lines = ["📋 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
    for o in orders:
        emoji = STATUS_EMOJI.get(o.get("status", ""), "❓")
        lines.append(
            f"{emoji} <b>#{o.get('smm_order_id')}</b>  {(o.get('service_name') or '')[:25]}\n"
            f"   🔢 {o.get('quantity', 0):,}  |  💰 {o.get('price_uzs', 0):,.0f} so'm\n"
        )
    await call.message.edit_text(
        "\n".join(lines), reply_markup=back_to_main(), parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "support")
async def cb_support(call: CallbackQuery):
    await call.message.edit_text(
        _support_text(),
        reply_markup=support_keyboard(ADMIN_USERNAME),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "referral")
async def cb_referral(call: CallbackQuery):
    stats    = await get_referral_stats(call.from_user.id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=REF_{call.from_user.id}"
    await call.message.edit_text(
        referral_text(stats, ref_link),
        reply_markup=referral_keyboard(call.from_user.id, BOT_USERNAME),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("referral_history_"))
async def cb_referral_history(call: CallbackQuery):
    import time as _time
    page      = int(call.data.split("_")[2])
    PAGE_SIZE = 5

    rows  = await get_referral_history(call.from_user.id, limit=PAGE_SIZE, offset=page * PAGE_SIZE)
    total = await get_referral_history_count(call.from_user.id)

    if not rows:
        await call.message.edit_text(
            "📋 <b>Referal tarixi</b>\n\nHali referal daromad yo'q.",
            reply_markup=referral_history_keyboard(page, False, False),
            parse_mode="HTML",
        )
        await call.answer()
        return

    start = page * PAGE_SIZE + 1
    end   = page * PAGE_SIZE + len(rows)
    lines = [f"📋 <b>Referal tarixi</b>  ({start}–{end} / {total})\n"]

    TYPE_ICON  = {"signup_bonus": "👤", "deposit_bonus": "💳", "percent": "📦"}
    TYPE_LABEL = {
        "signup_bonus":  "Ro'yxatdan o'tdi",
        "deposit_bonus": "Balans to'ldirdi",
        "percent":       "Buyurtma berdi",
    }

    for r in rows:
        icon  = TYPE_ICON.get(r["type"], "💸")
        label = TYPE_LABEL.get(r["type"], r["type"])
        name  = r.get("from_name") or f"ID:{r['from_user']}"
        ts    = _time.strftime("%d.%m.%Y", _time.localtime(r.get("created_at", 0)))
        lines.append(
            f"{icon} <b>+{r['amount']:,} so'm</b> — {name}\n"
            f"   {label}  •  {ts}"
        )

    has_prev = page > 0
    has_next = (page + 1) * PAGE_SIZE < total

    await call.message.edit_text(
        "\n".join(lines),
        reply_markup=referral_history_keyboard(page, has_prev, has_next),
        parse_mode="HTML",
    )
    await call.answer()


# ── Yordamchi ─────────────────────────────────────────────────

def _support_text() -> str:
    return (
        "🆘 <b>Yordam markazi</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "❓ <b>Buyurtma qancha vaqtda bajariladi?</b>\n"
        "➡️ 1 daqiqadan bir necha soatgacha\n\n"
        "❓ <b>Balans qanday to'ldiriladi?</b>\n"
        "➡️ Kartaga o'tkazma — chek 5 daqiqada\n"
        "    tasdiqlanadi\n\n"
        "❓ <b>Buyurtma bajarilmasa pul qaytadimi?</b>\n"
        "➡️ Ha, bajarilmagan qism balansingizga\n"
        "    avtomatik qaytariladi\n\n"
        "❓ <b>Minimal to'ldirish summasi?</b>\n"
        "➡️ 5,000 so'mdan boshlanadi\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💬 Boshqa savollar uchun admin bilan\n"
        "bog'laning 👇"
    )