"""
admin.py — Zendor SMM Bot
Admin panel — statistika, foydalanuvchilar, buyurtmalar, depozitlar.
2026 yangi dizayn.
"""

import os
import time
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import (
    get_users_stats, get_orders_stats, get_deposits_stats,
    get_top_users, get_pending_deposits, get_pool,
    get_all_orders_paginated, set_user_discount,
)
from keyboards.menus import admin_panel_keyboard, orders_filter_keyboard

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


def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


def _back_button(target: str = "adm_panel") -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="↩️  Orqaga", callback_data=target))
    return b


# ── Komandalar ────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🛠 <b>Admin panel</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Kerakli bo'limni tanlang 👇",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    u = await get_users_stats()
    o = await get_orders_stats()
    d = await get_deposits_stats()
    await message.answer(
        _stats_text(u, o, d),
        parse_mode="HTML",
        reply_markup=admin_panel_keyboard(),
    )


@router.message(Command("users"))
async def cmd_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    u = await get_users_stats()
    await message.answer(_users_text(u), parse_mode="HTML")


@router.message(Command("pending"))
async def cmd_pending(message: Message):
    if not is_admin(message.from_user.id):
        return
    deposits = await get_pending_deposits()
    await message.answer(_pending_text(deposits), parse_mode="HTML")


@router.message(Command("top"))
async def cmd_top(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await get_top_users(10)
    await message.answer(_top_text(users), parse_mode="HTML")


@router.message(Command("balance_check"))
async def cmd_balance_check(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "❌ <b>Foydalanish:</b> /balance_check &lt;user_id&gt;",
            parse_mode="HTML",
        )
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ User ID raqam bo'lishi kerak")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_id, full_name, username, balance, discount FROM users WHERE user_id=$1",
            uid,
        )
    if not row:
        await message.answer("❌ Foydalanuvchi topilmadi")
        return

    discount      = float(row["discount"] or 0)
    discount_line = f"\n🏷 Chegirma: <b>{discount:+.0f}%</b>" if discount != 0 else ""
    await message.answer(
        f"👤 <b>{row['full_name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID:       <code>{row['user_id']}</code>\n"
        f"📱 Username: @{row['username'] or '—'}\n"
        f"💰 Balans:   <b>{row['balance']:,} so'm</b>{discount_line}",
        parse_mode="HTML",
    )


@router.message(Command("add_balance"))
async def cmd_add_balance(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ <b>Foydalanish:</b> /add_balance &lt;user_id&gt; &lt;summa&gt;",
            parse_mode="HTML",
        )
        return
    try:
        uid, amount = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ Raqam bo'lishi kerak")
        return
    if amount <= 0:
        await message.answer("❌ Summa musbat bo'lishi kerak")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT full_name, balance FROM users WHERE user_id=$1", uid
        )
        if not row:
            await message.answer("❌ Foydalanuvchi topilmadi")
            return
        new_balance = int(row["balance"]) + amount
        await conn.execute(
            "UPDATE users SET balance = balance + $1 WHERE user_id = $2", amount, uid
        )

    try:
        await bot.send_message(
            uid,
            f"💰 <b>Balansingiz to'ldirildi!</b>\n\n"
            f"Admin tomonidan:\n"
            f"➕ <b>+{amount:,} so'm</b> tushdi.\n\n"
            f"💵 Yangi balans: <b>{new_balance:,} so'm</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await message.answer(
        f"✅ <b>{row['full_name']}</b> balansi to'ldirildi\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Oldingi:    <b>{int(row['balance']):,} so'm</b>\n"
        f"Qo'shildi:  <b>+{amount:,} so'm</b>\n"
        f"Yangi:      <b>{new_balance:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
    )


@router.message(Command("set_balance"))
async def cmd_set_balance(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ <b>Foydalanish:</b> /set_balance &lt;user_id&gt; &lt;yangi_balans&gt;",
            parse_mode="HTML",
        )
        return
    try:
        uid, new_balance = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ Raqam bo'lishi kerak")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT full_name, balance FROM users WHERE user_id=$1", uid
        )
        if not row:
            await message.answer("❌ Foydalanuvchi topilmadi")
            return
        old_balance = int(row["balance"])
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE user_id = $2", new_balance, uid
        )

    diff      = new_balance - old_balance
    diff_text = f"+{diff:,}" if diff >= 0 else f"{diff:,}"
    try:
        await bot.send_message(
            uid,
            f"💳 <b>Balansingiz o'zgartirildi!</b>\n\n"
            f"💵 Yangi balans: <b>{new_balance:,} so'm</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass
    await message.answer(
        f"✅ Balans o'rnatildi: <b>{row['full_name']}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Oldingi:    <b>{old_balance:,} so'm</b>\n"
        f"O'zgarish:  <b>{diff_text} so'm</b>\n"
        f"Yangi:      <b>{new_balance:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
    )


@router.message(Command("discount"))
async def cmd_discount(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ <b>Foydalanish:</b> /discount &lt;user_id&gt; &lt;foiz&gt;\n\n"
            "├ <b>+50</b> → narx 50% arzonlashadi\n"
            "├ <b>+100</b> → faqat tan narxi\n"
            "├ <b>0</b> → chegirma bekor\n"
            "└ <b>-30</b> → narx 30% qimmatlashadi\n\n"
            "Misol: /discount 123456789 50",
            parse_mode="HTML",
        )
        return
    try:
        uid, discount = int(parts[1]), float(parts[2])
    except ValueError:
        await message.answer("❌ Raqam bo'lishi kerak")
        return
    if not (-100 <= discount <= 100):
        await message.answer("❌ Foiz -100 dan 100 gacha bo'lishi kerak")
        return

    success = await set_user_discount(uid, discount)
    if not success:
        await message.answer("❌ Foydalanuvchi topilmadi")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name FROM users WHERE user_id=$1", uid)

    emoji = "🎁" if discount > 0 else ("🔄" if discount == 0 else "💸")
    desc  = (
        f"narxi {discount:.0f}% arzonlashadi" if discount > 0 else
        ("chegirma bekor qilindi" if discount == 0 else f"narxi {abs(discount):.0f}% qimmatlashadi")
    )
    await message.answer(
        f"{emoji} <b>{row['full_name']}</b> uchun:\n"
        f"🏷 Chegirma: <b>{discount:+.0f}%</b> — {desc}",
        parse_mode="HTML",
    )


# ── Callbacks ─────────────────────────────────────────────────

@router.callback_query(F.data == "adm_panel")
async def cb_adm_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await call.message.edit_text(
        "🛠 <b>Admin panel</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Kerakli bo'limni tanlang 👇",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "adm_users")
async def cb_adm_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    u = await get_users_stats()
    b = _back_button("adm_panel")
    await call.message.edit_text(
        _users_text(u),
        parse_mode="HTML",
        reply_markup=b.as_markup(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("adm_orders_"))
async def cb_adm_orders(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    parts         = call.data.split("_", 3)
    page          = int(parts[2])
    fkey          = parts[3]
    status_filter = None if fkey == "all" else fkey
    PAGE_SIZE     = 5

    orders, total = await get_all_orders_paginated(page, PAGE_SIZE, status_filter)
    start = page * PAGE_SIZE + 1
    end   = min((page + 1) * PAGE_SIZE, total)
    lines = [f"📦 <b>Buyurtmalar</b>  [{fkey}]  ({start}–{end} / {total})\n"]

    for o in orders:
        status_text = STATUS_UZ.get(o.get("status", ""), o.get("status", ""))
        name        = (o.get("full_name") or o.get("username") or f"ID:{o['user_id']}")[:18]
        svc         = (o.get("service_name") or "")[:22]
        ts          = time.strftime("%d.%m %H:%M", time.localtime(o.get("created_at", 0)))
        lines.append(
            f"🔖 <b>#{o.get('smm_order_id', o['id'])}</b>  {name}\n"
            f"   📌 {svc}\n"
            f"   🔢 {o.get('quantity',0):,}  |  💰 {o.get('price_uzs',0):,} so'm\n"
            f"   {status_text}  •  {ts}\n"
        )

    builder = orders_filter_keyboard(fkey, page)
    nav     = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"adm_orders_{page-1}_{fkey}"))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"adm_orders_{page+1}_{fkey}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="↩️  Orqaga", callback_data="adm_panel"))

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
    b = _back_button("adm_panel")
    await call.message.edit_text(
        f"💰 <b>Depozitlar statistikasi</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ Kutayotgan:        <b>{d['pending_count']}</b> ta  ({d['pending_sum']:,} so'm)\n"
        f"📅 Bugun tasdiqlangan: <b>{d['today_confirmed']:,} so'm</b>\n"
        f"✅ Jami tasdiqlangan:  <b>{d['confirmed_sum']:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML", reply_markup=b.as_markup(),
    )
    await call.answer()


@router.callback_query(F.data == "adm_top")
async def cb_adm_top(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    users = await get_top_users(10)
    b     = _back_button("adm_panel")
    await call.message.edit_text(
        _top_text(users),
        parse_mode="HTML",
        reply_markup=b.as_markup(),
    )
    await call.answer()


@router.callback_query(F.data == "adm_pending")
async def cb_adm_pending(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    deposits = await get_pending_deposits()
    b        = _back_button("adm_panel")
    await call.message.edit_text(
        _pending_text(deposits),
        parse_mode="HTML",
        reply_markup=b.as_markup(),
    )
    await call.answer()


# ── Matnlar ───────────────────────────────────────────────────

def _stats_text(u: dict, o: dict, d: dict) -> str:
    return (
        "📊 <b>Bot statistikasi</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 <b>Foydalanuvchilar:</b>\n"
        f"├ Jami:            <b>{u['total']:,}</b>\n"
        f"├ Bugun yangi:     <b>+{u['new_today']}</b>\n"
        f"├ Bu hafta:        <b>+{u['new_week']}</b>\n"
        f"├ Buyurtma berganlar: <b>{u['with_orders']}</b>\n"
        f"└ Hali xarid qilmaganlar: <b>{u['no_orders']}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 <b>Buyurtmalar:</b>\n"
        f"├ Jami:        <b>{o['total']:,}</b>\n"
        f"├ Bugun:       <b>{o['today_orders']}</b>  (+{o['today_revenue']:,} so'm)\n"
        f"├ Bajarilgan:  <b>{o['completed']}</b>\n"
        f"├ Jarayonda:   <b>{o['pending']}</b>\n"
        f"├ Bekor:       <b>{o['canceled']}</b>\n"
        f"└ Jami tushum: <b>{o['total_revenue']:,} so'm</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>Depozitlar:</b>\n"
        f"├ Kutayotgan:      <b>{d['pending_count']}</b>  ({d['pending_sum']:,} so'm)\n"
        f"├ Bugun tasdiqlangan: <b>{d['today_confirmed']:,} so'm</b>\n"
        f"└ Jami tasdiqlangan:  <b>{d['confirmed_sum']:,} so'm</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👛 Foydalanuvchilar balansi: <b>{u['total_balance']:,} so'm</b>"
    )


def _users_text(u: dict) -> str:
    return (
        "👥 <b>Foydalanuvchilar</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"Jami:                <b>{u['total']:,}</b>\n"
        f"Bugun yangi:         <b>+{u['new_today']}</b>\n"
        f"Bu hafta yangi:      <b>+{u['new_week']}</b>\n"
        f"Buyurtma berganlar:  <b>{u['with_orders']}</b>\n"
        f"Hali xarid qilmaganlar: <b>{u['no_orders']}</b>\n"
        f"Umumiy balans:       <b>{u['total_balance']:,} so'm</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )


def _top_text(users: list) -> str:
    MEDALS = ["🥇", "🥈", "🥉"]
    lines  = ["🏆 <b>Top 10 — eng ko'p xarid:</b>\n", "━━━━━━━━━━━━━━━━━━━━━"]
    for i, u in enumerate(users, 1):
        medal = MEDALS[i - 1] if i <= 3 else f"{i}."
        name  = u.get("full_name") or u.get("username") or f"ID:{u['user_id']}"
        lines.append(
            f"{medal} <b>{name}</b>\n"
            f"   📦 {u['order_count']} ta  |  💰 {u['total_spent']:,} so'm"
        )
    return "\n".join(lines)


def _pending_text(deposits: list) -> str:
    if not deposits:
        return "✅ <b>Kutayotgan depozitlar yo'q!</b>"
    lines = [f"⏳ <b>Kutayotgan: {len(deposits)} ta</b>\n", "━━━━━━━━━━━━━━━━━━━━━"]
    for d in deposits[:15]:
        ts = time.strftime("%d.%m %H:%M", time.localtime(d.get("created_at", 0)))
        lines.append(
            f"• <code>#{d['id']}</code>  {d.get('full_name','?')}\n"
            f"  💰 {d['amount']:,} so'm  •  {ts}"
        )
    if len(deposits) > 15:
        lines.append(f"\n... va yana <b>{len(deposits) - 15}</b> ta")
    return "\n".join(lines)