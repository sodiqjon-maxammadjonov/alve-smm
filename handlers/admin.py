import os
import time
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (
    get_users_stats, get_orders_stats, get_deposits_stats,
    get_top_users, get_pending_deposits, get_pool
)

router = Router()

ADMIN_IDS_RAW = os.getenv("ADMIN_ID", "7917217047")
try:
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]
except Exception:
    ADMIN_IDS = [int(ADMIN_IDS_RAW)]


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_panel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm_users"),
        InlineKeyboardButton(text="📦 Buyurtmalar", callback_data="adm_orders")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Depozitlar", callback_data="adm_deposits"),
        InlineKeyboardButton(text="🏆 Top 10", callback_data="adm_top")
    )
    builder.row(
        InlineKeyboardButton(text="⏳ Kutayotgan cheklar", callback_data="adm_pending"),
    )
    return builder.as_markup()


# ── /admin komandasi ───────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🛠 <b>Admin panel</b>\n\nNimani ko'rmoqchisiz?",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


# ── /stats — umumiy statistika ────────────────────────────────

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
        f"├ Hafta davomida: <b>+{u['new_week']}</b>\n"
        f"├ Buyurtma berganlari: <b>{u['with_orders']}</b>\n"
        f"└ Hech narsa olmagan: <b>{u['no_orders']}</b>\n\n"
        "📦 <b>Buyurtmalar:</b>\n"
        f"├ Jami: <b>{o['total']:,}</b>\n"
        f"├ Bugun: <b>{o['today_orders']}</b> (+{o['today_revenue']:,} so'm)\n"
        f"├ Bajarilgan: <b>{o['completed']}</b>\n"
        f"├ Jarayonda: <b>{o['pending']}</b>\n"
        f"└ Jami tushum: <b>{o['total_revenue']:,} so'm</b>\n\n"
        "💰 <b>Depozitlar:</b>\n"
        f"├ Kutayotgan: <b>{d['pending_count']}</b> ({d['pending_sum']:,} so'm)\n"
        f"├ Bugun tasdiqlangan: <b>{d['today_confirmed']:,} so'm</b>\n"
        f"└ Jami tasdiqlangan: <b>{d['confirmed_sum']:,} so'm</b>\n\n"
        f"👛 <b>Foydalanuvchilar balansi:</b> {u['total_balance']:,} so'm"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=admin_panel_keyboard())


# ── /users — foydalanuvchilar statistikasi ────────────────────

@router.message(Command("users"))
async def cmd_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    u = await get_users_stats()
    text = (
        "👥 <b>Foydalanuvchilar statistikasi</b>\n\n"
        f"📊 Jami ro'yxatdan o'tgan: <b>{u['total']:,}</b>\n"
        f"🆕 Bugun qo'shilgan: <b>+{u['new_today']}</b>\n"
        f"📅 Bu hafta: <b>+{u['new_week']}</b>\n\n"
        f"✅ Buyurtma berganlar: <b>{u['with_orders']}</b>\n"
        f"😴 Hech narsa olmaganlar: <b>{u['no_orders']}</b>\n\n"
        f"💰 Umumiy balanslar: <b>{u['total_balance']:,} so'm</b>"
    )
    await message.answer(text, parse_mode="HTML")


# ── /pending — kutayotgan depozitlar ─────────────────────────

@router.message(Command("pending"))
async def cmd_pending(message: Message):
    if not is_admin(message.from_user.id):
        return
    deposits = await get_pending_deposits()
    if not deposits:
        await message.answer("✅ Hozirda kutayotgan depozitlar yo'q!")
        return
    lines = [f"⏳ <b>Kutayotgan depozitlar ({len(deposits)} ta):</b>\n"]
    for d in deposits[:10]:
        ts = time.strftime("%d.%m %H:%M", time.localtime(d.get("created_at", 0)))
        lines.append(
            f"🔖 <b>#{d['id']}</b> | {d.get('full_name','?')} | "
            f"<b>{d['amount']:,} so'm</b> | {ts}"
        )
    if len(deposits) > 10:
        lines.append(f"\n... va yana {len(deposits) - 10} ta")
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── /top — top foydalanuvchilar ───────────────────────────────

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


# ── /balance_check <user_id> — foydalanuvchi balansi ─────────

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

    full_name = row["full_name"]
    user_id = row["user_id"]
    username = row["username"] or "yoq"
    balance = row["balance"]
    await message.answer(
        f"👤 <b>{full_name}</b>\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Username: @{username}\n"
        f"💰 Balans: <b>{balance:,} so'm</b>",
        parse_mode="HTML"
    )


# ── /add_balance <user_id> <summa> — balans qo'shish ─────────

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
            f"Admin tomonidan <b>+{amount:,} so'm</b> balansingizga tushdi.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await message.answer(
        f"✅ <b>{row['full_name']}</b> ga <b>{amount:,} so'm</b> qo'shildi!",
        parse_mode="HTML"
    )


# ── Callback handlerlari ──────────────────────────────────────

@router.callback_query(F.data == "adm_users")
async def cb_adm_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    u = await get_users_stats()
    text = (
        "👥 <b>Foydalanuvchilar statistikasi</b>\n\n"
        f"📊 Jami: <b>{u['total']:,}</b>\n"
        f"🆕 Bugun: <b>+{u['new_today']}</b>\n"
        f"📅 Bu hafta: <b>+{u['new_week']}</b>\n"
        f"✅ Buyurtma bergan: <b>{u['with_orders']}</b>\n"
        f"😴 Xarid qilmagan: <b>{u['no_orders']}</b>\n"
        f"💰 Umumiy balans: <b>{u['total_balance']:,} so'm</b>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
    await call.answer()


@router.callback_query(F.data == "adm_orders")
async def cb_adm_orders(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    o = await get_orders_stats()
    text = (
        "📦 <b>Buyurtmalar statistikasi</b>\n\n"
        f"📊 Jami: <b>{o['total']:,}</b>\n"
        f"📅 Bugun: <b>{o['today_orders']}</b> (+{o['today_revenue']:,} so'm)\n"
        f"✅ Bajarilgan: <b>{o['completed']}</b>\n"
        f"⏳ Jarayonda: <b>{o['pending']}</b>\n"
        f"💰 Jami tushum: <b>{o['total_revenue']:,} so'm</b>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
    await call.answer()


@router.callback_query(F.data == "adm_deposits")
async def cb_adm_deposits(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    d = await get_deposits_stats()
    text = (
        "💰 <b>Depozitlar statistikasi</b>\n\n"
        f"⏳ Kutayotgan: <b>{d['pending_count']}</b> ({d['pending_sum']:,} so'm)\n"
        f"📅 Bugun tasdiqlangan: <b>{d['today_confirmed']:,} so'm</b>\n"
        f"✅ Jami tasdiqlangan: <b>{d['confirmed_sum']:,} so'm</b>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
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
        lines.append(f"{i}. <b>{name}</b> — {u['total_spent']:,} so'm ({u['order_count']} ta)")
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_panel"))
    await call.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=builder.as_markup())
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
            "✅ Hozirda kutayotgan depozitlar yo'q!",
            reply_markup=builder.as_markup()
        )
        await call.answer()
        return
    lines = [f"⏳ <b>Kutayotgan: {len(deposits)} ta</b>\n"]
    for d in deposits[:10]:
        ts = time.strftime("%d.%m %H:%M", time.localtime(d.get("created_at", 0)))
        lines.append(f"• #{d['id']} | {d.get('full_name','?')} | {d['amount']:,} so'm | {ts}")
    await call.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=builder.as_markup())
    await call.answer()


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