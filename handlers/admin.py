import os
import time
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (
    get_users_stats, get_orders_stats, get_deposits_stats,
    get_top_users, get_pending_deposits, get_pool,
    get_all_orders_paginated
)

router = Router()

ADMIN_IDS_RAW = os.getenv("ADMIN_ID", "7917217047")
try:
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]
except Exception:
    ADMIN_IDS = [int(ADMIN_IDS_RAW)]

STATUS_UZ = {
    "Pending":     "⏳ Kutilmoqda",
    "In Progress": "🔄 Bajarilmoqda",
    "In progress": "🔄 Bajarilmoqda",
    "Processing":  "🔄 Jarayonda",
    "Completed":   "✅ Bajarildi",
    "Partial":     "⚠️ Qisman",
    "Canceled":    "❌ Bekor",
    "Cancelled":   "❌ Bekor",
    "Refunded":    "💸 Qaytarildi",
}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_panel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm_users"),
        InlineKeyboardButton(text="📦 Buyurtmalar", callback_data="adm_orders_0_all")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Depozitlar", callback_data="adm_deposits"),
        InlineKeyboardButton(text="🏆 Top 10", callback_data="adm_top")
    )
    builder.row(InlineKeyboardButton(text="⏳ Kutayotgan cheklar", callback_data="adm_pending"))
    return builder.as_markup()


def orders_filter_keyboard(current: str, page: int):
    builder = InlineKeyboardBuilder()
    filters = [
        ("Hammasi", "all"),
        ("⏳ Kutish", "Pending"),
        ("🔄 Jarayon", "In progress"),
        ("✅ Bajarildi", "Completed"),
        ("❌ Bekor", "Canceled"),
    ]
    row = []
    for label, key in filters:
        prefix = "▶ " if key == current else ""
        row.append(InlineKeyboardButton(
            text=f"{prefix}{label}",
            callback_data=f"adm_orders_0_{key}"
        ))
    builder.row(*row[:3])
    builder.row(*row[3:])
    return builder


# ── /admin ────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🛠 <b>Admin panel</b>\n\nNimani ko'rmoqchisiz?",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


# ── /stats ────────────────────────────────────────────────────

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    u = await get_users_stats()
    o = await get_orders_stats()
    d = await get_deposits_stats()
    text = (
        "📊 <b>Bot statistikasi</b>\n\n"
        "👥 <b>Foydalanuvchilar:</b>\n"
        f"├ Jami: <b>{u['total']:,}</b>\n"
        f"├ Bugun yangi: <b>+{u['new_today']}</b>\n"
        f"├ Bu hafta: <b>+{u['new_week']}</b>\n"
        f"├ Buyurtma berganlar: <b>{u['with_orders']}</b>\n"
        f"└ Xarid qilmaganlar: <b>{u['no_orders']}</b>\n\n"
        "📦 <b>Buyurtmalar:</b>\n"
        f"├ Jami: <b>{o['total']:,}</b>\n"
        f"├ Bugun: <b>{o['today_orders']}</b> (+{o['today_revenue']:,} so'm)\n"
        f"├ Bajarilgan: <b>{o['completed']}</b>\n"
        f"├ Jarayonda: <b>{o['pending']}</b>\n"
        f"├ Bekor qilingan: <b>{o['canceled']}</b>\n"
        f"└ Jami tushum: <b>{o['total_revenue']:,} so'm</b>\n\n"
        "💰 <b>Depozitlar:</b>\n"
        f"├ Kutayotgan: <b>{d['pending_count']}</b> ({d['pending_sum']:,} so'm)\n"
        f"├ Bugun tasdiqlangan: <b>{d['today_confirmed']:,} so'm</b>\n"
        f"└ Jami tasdiqlangan: <b>{d['confirmed_sum']:,} so'm</b>\n\n"
        f"👛 <b>Foydalanuvchilar balansi:</b> {u['total_balance']:,} so'm"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=admin_panel_keyboard())


# ── /users ────────────────────────────────────────────────────

@router.message(Command("users"))
async def cmd_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    u = await get_users_stats()
    await message.answer(
        "👥 <b>Foydalanuvchilar</b>\n\n"
        f"📊 Jami: <b>{u['total']:,}</b>\n"
        f"🆕 Bugun: <b>+{u['new_today']}</b>\n"
        f"📅 Bu hafta: <b>+{u['new_week']}</b>\n"
        f"✅ Buyurtma berganlar: <b>{u['with_orders']}</b>\n"
        f"😴 Xarid qilmaganlar: <b>{u['no_orders']}</b>\n"
        f"💰 Umumiy balans: <b>{u['total_balance']:,} so'm</b>",
        parse_mode="HTML"
    )


# ── /pending ──────────────────────────────────────────────────

@router.message(Command("pending"))
async def cmd_pending(message: Message):
    if not is_admin(message.from_user.id):
        return
    deposits = await get_pending_deposits()
    if not deposits:
        await message.answer("✅ Kutayotgan depozitlar yo'q!")
        return
    lines = [f"⏳ <b>Kutayotgan: {len(deposits)} ta</b>\n"]
    for d in deposits[:10]:
        ts = time.strftime("%d.%m %H:%M", time.localtime(d.get("created_at", 0)))
        lines.append(
            f"🔖 <b>#{d['id']}</b> | {d.get('full_name', '?')} | "
            f"<b>{d['amount']:,} so'm</b> | {ts}"
        )
    if len(deposits) > 10:
        lines.append(f"\n... va yana {len(deposits) - 10} ta")
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── /top ──────────────────────────────────────────────────────

@router.message(Command("top"))
async def cmd_top(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await get_top_users(10)
    lines = ["🏆 <b>Top 10 — eng ko'p xarid qilganlar:</b>\n"]
    for i, u in enumerate(users, 1):
        name = u.get("full_name") or u.get("username") or f"ID:{u['user_id']}"
        lines.append(
            f"{i}. <b>{name}</b>\n"
            f"   📦 {u['order_count']} buyurtma | 💰 {u['total_spent']:,} so'm"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── /balance_check ────────────────────────────────────────────

@router.message(Command("balance_check"))
async def cmd_balance_check(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Foydalanish: /balance_check <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ User ID raqam bo'lishi kerak")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_id, full_name, username, balance FROM users WHERE user_id=$1", uid
        )
    if not row:
        await message.answer("❌ Foydalanuvchi topilmadi")
        return
    await message.answer(
        f"👤 <b>{row['full_name']}</b>\n"
        f"🆔 ID: <code>{row['user_id']}</code>\n"
        f"👤 Username: @{row['username'] or 'yoq'}\n"
        f"💰 Balans: <b>{row['balance']:,} so'm</b>",
        parse_mode="HTML"
    )


# ── /add_balance ──────────────────────────────────────────────

@router.message(Command("add_balance"))
async def cmd_add_balance(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Foydalanish: /add_balance <user_id> <summa>")
        return
    try:
        uid = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("❌ User ID va summa raqam bo'lishi kerak")
        return
    if amount <= 0:
        await message.answer("❌ Summa musbat bo'lishi kerak")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name FROM users WHERE user_id=$1", uid)
        if not row:
            await message.answer("❌ Foydalanuvchi topilmadi")
            return
        await conn.execute(
            "UPDATE users SET balance = balance + $1 WHERE user_id = $2", amount, uid
        )

    try:
        await bot.send_message(
            uid,
            f"💰 <b>Balansingizga qo'shildi!</b>\n\n"
            f"Admin tomonidan <b>+{amount:,} so'm</b> tushdi.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await message.answer(
        f"✅ <b>{row['full_name']}</b> ga <b>{amount:,} so'm</b> qo'shildi!",
        parse_mode="HTML"
    )


# ── Callback: admin panel ─────────────────────────────────────

@router.callback_query(F.data == "adm_panel")
async def cb_adm_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await call.message.edit_text(
        "🛠 <b>Admin panel</b>\n\nNimani ko'rmoqchisiz?",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "adm_users")
async def cb_adm_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    u = await get_users_stats()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    await call.message.edit_text(
        "👥 <b>Foydalanuvchilar</b>\n\n"
        f"📊 Jami: <b>{u['total']:,}</b>\n"
        f"🆕 Bugun: <b>+{u['new_today']}</b>\n"
        f"📅 Bu hafta: <b>+{u['new_week']}</b>\n"
        f"✅ Buyurtma berganlar: <b>{u['with_orders']}</b>\n"
        f"😴 Xarid qilmaganlar: <b>{u['no_orders']}</b>\n"
        f"💰 Umumiy balans: <b>{u['total_balance']:,} so'm</b>",
        parse_mode="HTML", reply_markup=builder.as_markup()
    )
    await call.answer()


@router.callback_query(F.data.startswith("adm_orders_"))
async def cb_adm_orders(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    # format: adm_orders_{page}_{filter}
    parts = call.data.split("_", 3)
    page = int(parts[2])
    status_filter = parts[3] if parts[3] != "all" else None

    PAGE_SIZE = 5
    orders, total = await get_all_orders_paginated(page, PAGE_SIZE, status_filter)

    filter_label = parts[3]
    lines = [
        f"📦 <b>Buyurtmalar</b> [{filter_label}] "
        f"({page * PAGE_SIZE + 1}–{min((page + 1) * PAGE_SIZE, total)} / {total})\n"
    ]

    for o in orders:
        status_text = STATUS_UZ.get(o.get("status", ""), o.get("status", ""))
        name = (o.get("full_name") or o.get("username") or f"ID:{o['user_id']}")[:18]
        svc = (o.get("service_name") or "")[:22]
        ts = time.strftime("%d.%m %H:%M", time.localtime(o.get("created_at", 0)))
        lines.append(
            f"🔖 <b>#{o.get('smm_order_id', o['id'])}</b> | {name}\n"
            f"   📌 {svc}\n"
            f"   🔢 {o.get('quantity', 0):,} | 💰 {o.get('price_uzs', 0):,} so'm\n"
            f"   {status_text} | {ts}\n"
        )

    # Filtr tugmalari
    builder = orders_filter_keyboard(parts[3], page)

    # Sahifalash
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="⬅️ Oldingi", callback_data=f"adm_orders_{page - 1}_{parts[3]}"
        ))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(InlineKeyboardButton(
            text="Keyingi ➡️", callback_data=f"adm_orders_{page + 1}_{parts[3]}"
        ))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))

    await call.message.edit_text(
        "\n".join(lines), parse_mode="HTML", reply_markup=builder.as_markup()
    )
    await call.answer()


@router.callback_query(F.data == "adm_deposits")
async def cb_adm_deposits(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    d = await get_deposits_stats()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    await call.message.edit_text(
        "💰 <b>Depozitlar</b>\n\n"
        f"⏳ Kutayotgan: <b>{d['pending_count']}</b> ({d['pending_sum']:,} so'm)\n"
        f"📅 Bugun tasdiqlangan: <b>{d['today_confirmed']:,} so'm</b>\n"
        f"✅ Jami tasdiqlangan: <b>{d['confirmed_sum']:,} so'm</b>",
        parse_mode="HTML", reply_markup=builder.as_markup()
    )
    await call.answer()


@router.callback_query(F.data == "adm_top")
async def cb_adm_top(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    users = await get_top_users(10)
    lines = ["🏆 <b>Top 10 mijozlar:</b>\n"]
    for i, u in enumerate(users, 1):
        name = u.get("full_name") or u.get("username") or f"ID:{u['user_id']}"
        lines.append(
            f"{i}. <b>{name}</b> — {u['total_spent']:,} so'm ({u['order_count']} ta)"
        )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    await call.message.edit_text(
        "\n".join(lines), parse_mode="HTML", reply_markup=builder.as_markup()
    )
    await call.answer()


@router.callback_query(F.data == "adm_pending")
async def cb_adm_pending(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    deposits = await get_pending_deposits()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    if not deposits:
        await call.message.edit_text(
            "✅ Kutayotgan depozitlar yo'q!",
            reply_markup=builder.as_markup()
        )
        await call.answer()
        return
    lines = [f"⏳ <b>Kutayotgan: {len(deposits)} ta</b>\n"]
    for d in deposits[:10]:
        ts = time.strftime("%d.%m %H:%M", time.localtime(d.get("created_at", 0)))
        lines.append(
            f"• #{d['id']} | {d.get('full_name', '?')} | {d['amount']:,} so'm | {ts}"
        )
    await call.message.edit_text(
        "\n".join(lines), parse_mode="HTML", reply_markup=builder.as_markup()
    )
    await call.answer()