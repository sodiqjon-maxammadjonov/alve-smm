"""
handlers/admin.py — Zendor SMM Bot
Admin panel — statistika, foydalanuvchilar, buyurtmalar, depozitlar.

Admin komandalar:
  /admin            — Admin panel (inline menyu)
  /stats            — To'liq statistika
  /userinfo <id>    — User haqida to'liq ma'lumot + tugmalar
  /userorders <id>  — User buyurtmalari
  /userstats <id>   — User statistikasi
  /add_balance      — Balans qo'shish
  /set_balance      — Balansni o'rnatish
  /discount         — Chegirma o'rnatish
  /ban <id>         — Bloklash
  /unban <id>       — Blokni ochish
  /pending          — Kutayotgan depozitlar
  /top              — Top 10 mijozlar
  /smm_balance      — SMM panel balansi
"""

import os
import time
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import (
    get_users_stats, get_orders_stats, get_deposits_stats,
    get_top_users, get_pending_deposits, get_pool,
    get_all_orders_paginated, set_user_discount,
    get_user_orders, get_referral_stats,
)
from keyboards.menus import (
    admin_panel_keyboard, orders_filter_keyboard,
    back_to_main,
)
from core.constants import STATUS_UZ, DIVIDER
from core.smm_api import get_smm_balance

router = Router()

_admin_raw = os.getenv("ADMIN_ID", "7917217047")
try:
    ADMIN_IDS: list[int] = [int(x.strip()) for x in _admin_raw.split(",")]
except Exception:
    ADMIN_IDS = [int(_admin_raw)]

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")


def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# ── Yordamchi keyboardlar ─────────────────────────────────────

def _back_btn(target: str = "adm_panel") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="↩️  Orqaga",    callback_data=target),
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return b.as_markup()


def _user_action_keyboard(uid: int) -> InlineKeyboardMarkup:
    """
    /userinfo tugmalari — barcha handlerlari yozilgan:
      📦 Buyurtmalari   → cb_adm_uorders
      📊 Statistika     → cb_adm_ustats
      ➕ Balans qo'shish → cb_adm_addbal  (FSM)
      🏷 Chegirma       → cb_adm_disc     (FSM)
      💬 Xabar yuborish → cb_adm_msg      (FSM)
    """
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text="📦 Buyurtmalari",
            callback_data=f"adm_uorders_{uid}_0",
        ),
        InlineKeyboardButton(
            text="📊 Statistika",
            callback_data=f"adm_ustats_{uid}",
        ),
    )
    b.row(
        InlineKeyboardButton(
            text="➕ Balans qo'shish",
            callback_data=f"adm_addbal_{uid}",
        ),
        InlineKeyboardButton(
            text="🏷 Chegirma",
            callback_data=f"adm_disc_{uid}",
        ),
    )
    b.row(
        InlineKeyboardButton(
            text="💬 Xabar yuborish",
            callback_data=f"adm_msg_{uid}",
        ),
    )
    b.row(
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return b.as_markup()


def _user_orders_keyboard(
    uid: int, page: int, has_prev: bool, has_next: bool
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    nav = []
    if has_prev:
        nav.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"adm_uorders_{uid}_{page - 1}")
        )
    if has_next:
        nav.append(
            InlineKeyboardButton(text="➡️", callback_data=f"adm_uorders_{uid}_{page + 1}")
        )
    if nav:
        b.row(*nav)
    b.row(
        InlineKeyboardButton(text="↩️  Profil",    callback_data=f"adm_uprofile_{uid}"),
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return b.as_markup()


# ── FSM holatlari ─────────────────────────────────────────────

class AdminMsgState(StatesGroup):
    waiting_text = State()


class AdminAddBalState(StatesGroup):
    waiting_amount = State()


class AdminDiscState(StatesGroup):
    waiting_discount = State()


# ═══════════════════════════════════════════════════════════════
#  KOMANDALAR
# ═══════════════════════════════════════════════════════════════

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        f"🛠 <b>Admin panel</b>\n\n{DIVIDER}\nKerakli bo'limni tanlang 👇",
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


# ── /userinfo ─────────────────────────────────────────────────

@router.message(Command("userinfo"))
async def cmd_userinfo(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ <b>Foydalanish:</b>\n"
            "<code>/userinfo 123456789</code>\n"
            "<code>/userinfo @username</code>",
            parse_mode="HTML",
        )
        return

    pool      = await get_pool()
    query_val = parts[1].strip().lstrip("@")

    async with pool.acquire() as conn:
        if query_val.isdigit():
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1", int(query_val)
            )
        else:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE LOWER(username) = LOWER($1)", query_val
            )

    if not row:
        await message.answer("❌ Foydalanuvchi topilmadi.", parse_mode="HTML")
        return

    uid = row["user_id"]
    await message.answer(
        await _build_userinfo_text(uid, row),
        parse_mode="HTML",
        reply_markup=_user_action_keyboard(uid),
    )


async def _build_userinfo_text(uid: int, row=None) -> str:
    """User info matnini yaratadi. row=None bo'lsa DB dan o'qiydi."""
    if row is None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", uid)
        if not row:
            return "❌ Foydalanuvchi topilmadi."

    orders   = await get_user_orders(uid, limit=5)
    ref_st   = await get_referral_stats(uid)
    discount = float(row["discount"] or 0)

    last_order_str = (
        time.strftime("%d.%m.%Y %H:%M", time.localtime(orders[0]["created_at"]))
        if orders else "—"
    )
    reg_date      = time.strftime("%d.%m.%Y %H:%M", time.localtime(row["created_at"] or 0))
    discount_line = f"\n🏷 Chegirma:         <b>{discount:+.0f}%</b>" if discount != 0 else ""
    ref_line = (
        f"└ Referal egasi:  <code>{row['referred_by']}</code>"
        if row.get("referred_by") else
        "└ Referal:        <b>Yo'q</b>"
    )
    banned   = row.get("banned", False)
    ban_line = "\n🚫 <b>BLOKLANGAN</b>" if banned else ""

    return (
        f"👤 <b>Foydalanuvchi ma'lumoti</b>{ban_line}\n\n"
        f"{DIVIDER}\n"
        f"📛 Ism:             <b>{row['full_name'] or '—'}</b>\n"
        f"🆔 ID:              <code>{uid}</code>\n"
        f"📱 Username:        <b>{'@' + row['username'] if row['username'] else '—'}</b>\n"
        f"📅 Ro'yxat:         <b>{reg_date}</b>\n"
        f"{DIVIDER}\n"
        f"💰 Balans:          <b>{row['balance']:,} so'm</b>{discount_line}\n"
        f"{DIVIDER}\n"
        f"📦 Buyurtmalar:     <b>{len(orders)} ta (so'nggi 5)</b>\n"
        f"🕐 Oxirgi buyurtma: <b>{last_order_str}</b>\n"
        f"{DIVIDER}\n"
        f"🎁 Referal taklif:  <b>{ref_st['invited']} kishi</b>\n"
        f"💸 Referal daromad: <b>{ref_st['total_earned']:,} so'm</b>\n"
        f"{ref_line}\n"
        f"{DIVIDER}"
    )


# ── /userorders ───────────────────────────────────────────────

@router.message(Command("userorders"))
async def cmd_userorders(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer(
            "❌ <b>Foydalanish:</b> <code>/userorders 123456789</code>",
            parse_mode="HTML",
        )
        return
    uid          = int(parts[1])
    text, markup = await _build_uorders(uid, 0)
    await message.answer(text, parse_mode="HTML", reply_markup=markup)


async def _build_uorders(uid: int, page: int) -> tuple[str, InlineKeyboardMarkup]:
    """User buyurtmalari matni va klaviaturasi."""
    PAGE_SIZE = 8
    pool      = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM orders WHERE user_id=$1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
            uid, PAGE_SIZE, page * PAGE_SIZE,
        )
        total = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM orders WHERE user_id=$1", uid
        ))["cnt"])

    if not rows:
        return (
            f"📦 <b>Buyurtmalar</b>  <code>#{uid}</code>\n\nBuyurtma yo'q.",
            _user_orders_keyboard(uid, page, False, False),
        )

    start = page * PAGE_SIZE + 1
    end   = page * PAGE_SIZE + len(rows)
    lines = [
        f"📦 <b>Buyurtmalar</b>  <code>#{uid}</code>  ({start}–{end} / {total})\n",
        DIVIDER,
    ]
    for o in rows:
        status = STATUS_UZ.get(o.get("status", ""), o.get("status", ""))
        ts     = time.strftime("%d.%m %H:%M", time.localtime(o.get("created_at", 0)))
        lines.append(
            f"🔖 <b>#{o.get('smm_order_id', o['id'])}</b>  {(o.get('service_name') or '')[:22]}\n"
            f"   🔢 {o.get('quantity', 0):,}  |  💰 {o.get('price_uzs', 0):,} so'm\n"
            f"   {status}  •  {ts}"
        )

    has_prev = page > 0
    has_next = (page + 1) * PAGE_SIZE < total
    return "\n".join(lines), _user_orders_keyboard(uid, page, has_prev, has_next)


# ── /userstats ────────────────────────────────────────────────

@router.message(Command("userstats"))
async def cmd_userstats(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer(
            "❌ <b>Foydalanish:</b> <code>/userstats 123456789</code>",
            parse_mode="HTML",
        )
        return
    uid  = int(parts[1])
    text = await _build_ustats_text(uid)
    await message.answer(text, parse_mode="HTML", reply_markup=back_to_main())


async def _build_ustats_text(uid: int) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", uid)
        if not user:
            return "❌ Foydalanuvchi topilmadi."
        order_count = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM orders WHERE user_id=$1", uid))["cnt"])
        total_spent = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(price_uzs),0) AS s FROM orders WHERE user_id=$1", uid))["s"])
        dep_count   = int((await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM deposits WHERE user_id=$1 AND status='confirmed'", uid))["cnt"])
        dep_sum     = int((await conn.fetchrow(
            "SELECT COALESCE(SUM(amount),0) AS s FROM deposits WHERE user_id=$1 AND status='confirmed'", uid))["s"])

    ref_st = await get_referral_stats(uid)
    return (
        f"📊 <b>Foydalanuvchi statistikasi</b>\n\n"
        f"{DIVIDER}\n"
        f"👤 <b>{user['full_name'] or '—'}</b>  (<code>{uid}</code>)\n"
        f"{DIVIDER}\n"
        f"💰 Joriy balans:    <b>{user['balance']:,} so'm</b>\n"
        f"📦 Jami buyurtma:   <b>{order_count} ta</b>\n"
        f"💸 Jami sarflagan:  <b>{total_spent:,} so'm</b>\n"
        f"{DIVIDER}\n"
        f"💳 Depozit soni:    <b>{dep_count} ta</b>\n"
        f"💳 Jami depozit:    <b>{dep_sum:,} so'm</b>\n"
        f"{DIVIDER}\n"
        f"🎁 Referal taklif:  <b>{ref_st['invited']} kishi</b>\n"
        f"💰 Referal daromad: <b>{ref_st['total_earned']:,} so'm</b>\n"
        f"{DIVIDER}"
    )


# ── /add_balance ──────────────────────────────────────────────

@router.message(Command("add_balance"))
async def cmd_add_balance(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ <b>Foydalanish:</b> <code>/add_balance 123456789 50000</code>",
            parse_mode="HTML",
        )
        return
    try:
        uid, amount = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ ID va summa raqam bo'lishi kerak!")
        return
    if amount == 0:
        await message.answer("❌ Summa 0 bo'lishi mumkin emas!")
        return
    await _do_add_balance(message, bot, uid, amount)


async def _do_add_balance(responder, bot: Bot, uid: int, amount: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name, balance FROM users WHERE user_id=$1", uid)
        if not row:
            await responder.answer("❌ Foydalanuvchi topilmadi!")
            return
        new_bal = int(row["balance"]) + amount
        await conn.execute("UPDATE users SET balance=balance+$1 WHERE user_id=$2", amount, uid)

    sign = "➕" if amount > 0 else "➖"
    try:
        await bot.send_message(
            uid,
            f"💰 <b>Balansingiz yangilandi!</b>\n\n"
            f"Admin tomonidan: {sign} <b>{abs(amount):,} so'm</b>\n\n"
            f"💵 Yangi balans: <b>{new_bal:,} so'm</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await responder.answer(
        f"✅ <b>{row['full_name']}</b> balansi yangilandi\n\n"
        f"{DIVIDER}\n"
        f"Oldingi:   <b>{int(row['balance']):,} so'm</b>\n"
        f"O'zgarish: <b>{'+'if amount>0 else ''}{amount:,} so'm</b>\n"
        f"Yangi:     <b>{new_bal:,} so'm</b>\n"
        f"{DIVIDER}",
        parse_mode="HTML",
    )


# ── /set_balance ──────────────────────────────────────────────

@router.message(Command("set_balance"))
async def cmd_set_balance(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ <b>Foydalanish:</b> <code>/set_balance 123456789 100000</code>",
            parse_mode="HTML",
        )
        return
    try:
        uid, new_bal = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ Raqam bo'lishi kerak!")
        return
    if new_bal < 0:
        await message.answer("❌ Balans manfiy bo'lishi mumkin emas!")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name, balance FROM users WHERE user_id=$1", uid)
        if not row:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            return
        old_bal = int(row["balance"])
        await conn.execute("UPDATE users SET balance=$1 WHERE user_id=$2", new_bal, uid)

    diff = new_bal - old_bal
    try:
        await bot.send_message(
            uid,
            f"💰 <b>Balansingiz o'rnatildi!</b>\n\n"
            f"Admin tomonidan:\n"
            f"💵 Yangi balans: <b>{new_bal:,} so'm</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await message.answer(
        f"✅ <b>{row['full_name']}</b> balansi o'rnatildi\n\n"
        f"{DIVIDER}\n"
        f"Oldingi:   <b>{old_bal:,} so'm</b>\n"
        f"O'zgarish: <b>{'+'if diff>=0 else ''}{diff:,} so'm</b>\n"
        f"Yangi:     <b>{new_bal:,} so'm</b>\n"
        f"{DIVIDER}",
        parse_mode="HTML",
    )


# ── /discount ─────────────────────────────────────────────────

@router.message(Command("discount"))
async def cmd_discount(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            f"❌ <b>Foydalanish:</b> <code>/discount 123456789 30</code>\n\n"
            f"{DIVIDER}\n"
            "├ <b>50</b>  → narx 50% arzonlashadi\n"
            "├ <b>0</b>   → chegirma bekor qilinadi\n"
            "└ <b>-30</b> → narx 30% qimmatlashadi",
            parse_mode="HTML",
        )
        return
    try:
        uid, discount = int(parts[1]), float(parts[2])
    except ValueError:
        await message.answer("❌ Raqam bo'lishi kerak!")
        return
    if not (-100 <= discount <= 100):
        await message.answer("❌ Foiz -100 dan 100 gacha bo'lishi kerak!")
        return
    await _do_set_discount(message, bot, uid, discount)


async def _do_set_discount(responder, bot: Bot, uid: int, discount: float) -> None:
    ok = await set_user_discount(uid, discount)
    if not ok:
        await responder.answer("❌ Foydalanuvchi topilmadi!")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name FROM users WHERE user_id=$1", uid)

    if discount > 0:
        emoji, desc = "🎁", f"narxi {discount:.0f}% arzonlashadi"
    elif discount == 0:
        emoji, desc = "🔄", "chegirma bekor qilindi"
    else:
        emoji, desc = "💸", f"narxi {abs(discount):.0f}% qimmatlashadi"

    await responder.answer(
        f"{emoji} <b>{row['full_name']}</b>\n"
        f"🏷 Chegirma: <b>{discount:+.0f}%</b> — {desc}",
        parse_mode="HTML",
    )
    if discount != 0:
        try:
            await bot.send_message(
                uid,
                f"🎁 <b>Chegirma berildi!</b>\n\n"
                f"Admin siz uchun <b>{discount:+.0f}%</b> chegirma o'rnatdi!\n"
                f"Endi {desc}.",
                parse_mode="HTML",
            )
        except Exception:
            pass


# ── /ban / /unban ─────────────────────────────────────────────

@router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("❌ <b>Foydalanish:</b> <code>/ban 123456789</code>", parse_mode="HTML")
        return
    uid  = int(parts[1])
    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS banned BOOLEAN DEFAULT FALSE"
            )
        except Exception:
            pass
        row = await conn.fetchrow("SELECT full_name FROM users WHERE user_id=$1", uid)
        if not row:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            return
        await conn.execute("UPDATE users SET banned=TRUE WHERE user_id=$1", uid)

    try:
        await bot.send_message(
            uid,
            "⛔ <b>Hisobingiz bloklandi.</b>\n\nMuammo bo'lsa admin bilan bog'laning.",
            parse_mode="HTML",
        )
    except Exception:
        pass
    await message.answer(
        f"⛔ <b>{row['full_name']}</b> (<code>{uid}</code>) bloklandi.", parse_mode="HTML"
    )


@router.message(Command("unban"))
async def cmd_unban(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("❌ <b>Foydalanish:</b> <code>/unban 123456789</code>", parse_mode="HTML")
        return
    uid  = int(parts[1])
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name FROM users WHERE user_id=$1", uid)
        if not row:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            return
        await conn.execute("UPDATE users SET banned=FALSE WHERE user_id=$1", uid)

    try:
        await bot.send_message(
            uid,
            "✅ <b>Hisobingiz blokdan chiqarildi!</b>\n\nBotdan foydalanishingiz mumkin.",
            parse_mode="HTML",
        )
    except Exception:
        pass
    await message.answer(
        f"✅ <b>{row['full_name']}</b> (<code>{uid}</code>) blokdan chiqarildi.", parse_mode="HTML"
    )


# ── /pending / /top / /smm_balance ───────────────────────────

@router.message(Command("pending"))
async def cmd_pending(message: Message):
    if not is_admin(message.from_user.id):
        return
    deposits = await get_pending_deposits()
    await message.answer(_pending_text(deposits), parse_mode="HTML", reply_markup=back_to_main())


@router.message(Command("top"))
async def cmd_top(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await get_top_users(10)
    await message.answer(_top_text(users), parse_mode="HTML", reply_markup=back_to_main())


@router.message(Command("backup"))
async def cmd_backup(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    await message.answer("⏳ Backup tayyorlanmoqda...")
    from main import send_backup
    ok = await send_backup(bot, requester_id=message.from_user.id)
    if ok:
        await message.answer("✅ Backup muvaffaqiyatli yuborildi!")
    else:
        await message.answer("❌ Backup yuborishda xato. GROUP_ID to'g'riligini tekshiring.")


@router.message(Command("set_balance_mute"))
async def cmd_set_balance_mute(message: Message):
    """Foydalanuvchiga xabar yubormasdan balansini o'rnatish."""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ <b>Foydalanish:</b> <code>/set_balance_mute 123456789 100000</code>\n\n"
            "Foydalanuvchiga <b>xabar yuborilmaydi</b>.",
            parse_mode="HTML",
        )
        return
    try:
        uid, new_bal = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ Raqam bo'lishi kerak!")
        return
    if new_bal < 0:
        await message.answer("❌ Balans manfiy bo'lishi mumkin emas!")
        return

    from database import set_balance, get_user
    user = await get_user(uid)
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi!")
        return
    old_bal = await set_balance(uid, new_bal)
    diff    = new_bal - old_bal

    await message.answer(
        f"🔇 <b>{user['full_name']}</b> balansi yangilandi <i>(xabarsiz)</i>\n\n"
        f"{DIVIDER}\n"
        f"Oldingi:   <b>{old_bal:,} so'm</b>\n"
        f"O'zgarish: <b>{'+'if diff>=0 else ''}{diff:,} so'm</b>\n"
        f"Yangi:     <b>{new_bal:,} so'm</b>\n"
        f"{DIVIDER}",
        parse_mode="HTML",
    )


@router.message(Command("smm_balance"))
async def cmd_smm_balance(message: Message):
    if not is_admin(message.from_user.id):
        return
    bal_usd = await get_smm_balance()
    from config import USD_TO_UZS
    bal_uzs = bal_usd * USD_TO_UZS
    await message.answer(
        f"💵 <b>SMM Panel balansi</b>\n\n"
        f"{DIVIDER}\n"
        f"🇺🇸 USD: <b>${bal_usd:.4f}</b>\n"
        f"🇺🇿 UZS: <b>{bal_uzs:,.0f} so'm</b>\n"
        f"{DIVIDER}\n\n"
        f"<i>Kurs: 1 USD = {USD_TO_UZS:,} so'm</i>",
        parse_mode="HTML",
        reply_markup=back_to_main(),
    )


# ═══════════════════════════════════════════════════════════════
#  CALLBACK HANDLERLARI — Admin panel
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_panel")
async def cb_adm_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await call.message.edit_text(
        f"🛠 <b>Admin panel</b>\n\n{DIVIDER}\nKerakli bo'limni tanlang 👇",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "adm_stats")
async def cb_adm_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    u = await get_users_stats()
    o = await get_orders_stats()
    d = await get_deposits_stats()
    await call.message.edit_text(
        _stats_text(u, o, d), parse_mode="HTML", reply_markup=_back_btn("adm_panel")
    )
    await call.answer()


@router.callback_query(F.data == "adm_users")
async def cb_adm_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    u = await get_users_stats()
    await call.message.edit_text(
        _users_text(u), parse_mode="HTML", reply_markup=_back_btn("adm_panel")
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
    lines = [f"📦 <b>Buyurtmalar</b>  [{fkey}]  ({start}–{end} / {total})\n", DIVIDER]

    for o in orders:
        st   = STATUS_UZ.get(o.get("status", ""), o.get("status", ""))
        name = (o.get("full_name") or o.get("username") or f"ID:{o['user_id']}")[:18]
        svc  = (o.get("service_name") or "")[:22]
        ts   = time.strftime("%d.%m %H:%M", time.localtime(o.get("created_at", 0)))
        lines.append(
            f"🔖 <b>#{o.get('smm_order_id', o['id'])}</b>  {name}\n"
            f"   📌 {svc}\n"
            f"   🔢 {o.get('quantity', 0):,}  |  💰 {o.get('price_uzs', 0):,} so'm\n"
            f"   {st}  •  {ts}"
        )

    builder = orders_filter_keyboard(fkey, page)
    nav = []
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
    await call.message.edit_text(
        f"💰 <b>Depozitlar statistikasi</b>\n\n"
        f"{DIVIDER}\n"
        f"⏳ Kutayotgan:         <b>{d['pending_count']}</b> ta  ({d['pending_sum']:,} so'm)\n"
        f"📅 Bugun tasdiqlangan:  <b>{d['today_confirmed']:,} so'm</b>\n"
        f"✅ Jami tasdiqlangan:   <b>{d['confirmed_sum']:,} so'm</b>\n"
        f"{DIVIDER}",
        parse_mode="HTML",
        reply_markup=_back_btn("adm_panel"),
    )
    await call.answer()


@router.callback_query(F.data == "adm_top")
async def cb_adm_top(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    users = await get_top_users(10)
    await call.message.edit_text(
        _top_text(users), parse_mode="HTML", reply_markup=_back_btn("adm_panel")
    )
    await call.answer()


@router.callback_query(F.data == "adm_pending")
async def cb_adm_pending(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    deposits = await get_pending_deposits()
    await call.message.edit_text(
        _pending_text(deposits), parse_mode="HTML", reply_markup=_back_btn("adm_panel")
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════════
#  CALLBACK HANDLERLARI — User profil tugmalari
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("adm_uprofile_"))
async def cb_adm_uprofile(call: CallbackQuery):
    """↩️ Profil tugmasi — userinfo ga qaytish."""
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    uid  = int(call.data.split("_")[2])
    text = await _build_userinfo_text(uid)
    try:
        await call.message.edit_text(
            text, parse_mode="HTML", reply_markup=_user_action_keyboard(uid)
        )
    except Exception:
        await call.message.answer(
            text, parse_mode="HTML", reply_markup=_user_action_keyboard(uid)
        )
    await call.answer()


@router.callback_query(F.data.startswith("adm_uorders_"))
async def cb_adm_uorders(call: CallbackQuery):
    """📦 Buyurtmalari tugmasi."""
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    # format: adm_uorders_{uid}_{page}
    parts = call.data.split("_")
    uid   = int(parts[2])
    page  = int(parts[3]) if len(parts) > 3 else 0

    text, markup = await _build_uorders(uid, page)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=markup)
    await call.answer()


@router.callback_query(F.data.startswith("adm_ustats_"))
async def cb_adm_ustats(call: CallbackQuery):
    """📊 Statistika tugmasi."""
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    uid  = int(call.data.split("_")[2])
    text = await _build_ustats_text(uid)

    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="↩️  Profil",    callback_data=f"adm_uprofile_{uid}"),
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=b.as_markup())
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=b.as_markup())
    await call.answer()


@router.callback_query(F.data.startswith("adm_addbal_"))
async def cb_adm_addbal(call: CallbackQuery, state: FSMContext):
    """➕ Balans qo'shish — FSM."""
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    uid = int(call.data.split("_")[2])
    await state.update_data(target_uid=uid)
    await state.set_state(AdminAddBalState.waiting_amount)
    await call.message.answer(
        f"➕ <b>Balans qo'shish</b>\n\n"
        f"Foydalanuvchi: <code>{uid}</code>\n\n"
        f"Summani kiriting:\n"
        f"<i>(Manfiy ham bo'lishi mumkin, masalan: -5000)</i>\n\n"
        f"Bekor qilish: /cancel",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(AdminAddBalState.waiting_amount)
async def process_admin_addbal(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("✅ Bekor qilindi.")
        return
    text = message.text.strip().replace(" ", "").replace(",", "") if message.text else ""
    try:
        amount = int(text)
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting! (masalan: 50000 yoki -10000)")
        return

    data = await state.get_data()
    uid  = data["target_uid"]
    await state.clear()
    await _do_add_balance(message, bot, uid, amount)


@router.callback_query(F.data.startswith("adm_disc_"))
async def cb_adm_disc(call: CallbackQuery, state: FSMContext):
    """🏷 Chegirma o'rnatish — FSM."""
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    uid = int(call.data.split("_")[2])
    await state.update_data(target_uid=uid)
    await state.set_state(AdminDiscState.waiting_discount)
    await call.message.answer(
        f"🏷 <b>Chegirma o'rnatish</b>\n\n"
        f"Foydalanuvchi: <code>{uid}</code>\n\n"
        f"Chegirma foizini kiriting:\n"
        f"├ <b>50</b>  → 50% arzon\n"
        f"├ <b>0</b>   → chegirma yo'q\n"
        f"└ <b>-30</b> → 30% qimmat\n\n"
        f"Bekor qilish: /cancel",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(AdminDiscState.waiting_discount)
async def process_admin_disc(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("✅ Bekor qilindi.")
        return
    try:
        discount = float(message.text.strip())
    except (ValueError, AttributeError):
        await message.answer("❌ Faqat raqam kiriting!")
        return
    if not (-100 <= discount <= 100):
        await message.answer("❌ -100 dan 100 gacha bo'lishi kerak!")
        return

    data = await state.get_data()
    uid  = data["target_uid"]
    await state.clear()
    await _do_set_discount(message, bot, uid, discount)


@router.callback_query(F.data.startswith("adm_msg_"))
async def cb_adm_msg(call: CallbackQuery, state: FSMContext):
    """💬 Userga xabar yuborish — FSM."""
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    uid = int(call.data.split("_")[2])
    await state.update_data(target_uid=uid)
    await state.set_state(AdminMsgState.waiting_text)
    await call.message.answer(
        f"💬 <b>Xabar yuborish</b>\n\n"
        f"Foydalanuvchi: <code>{uid}</code>\n\n"
        f"Xabarni yozing yoki forward qiling:\n"
        f"<i>Bekor qilish: /cancel</i>",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(AdminMsgState.waiting_text)
async def process_admin_msg(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("✅ Bekor qilindi.")
        return

    data = await state.get_data()
    uid  = data["target_uid"]
    await state.clear()

    try:
        await bot.copy_message(
            chat_id=uid,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        await message.answer(
            f"✅ Xabar <code>{uid}</code> ga yuborildi!",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(
            f"❌ Xabar yuborib bo'lmadi.\n<code>{e}</code>",
            parse_mode="HTML",
        )


# ═══════════════════════════════════════════════════════════════
#  MATN FORMATLASH FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════

def _stats_text(u: dict, o: dict, d: dict) -> str:
    return (
        f"📊 <b>Bot statistikasi</b>\n\n"
        f"{DIVIDER}\n"
        "👥 <b>Foydalanuvchilar:</b>\n"
        f"├ Jami:                    <b>{u['total']:,}</b>\n"
        f"├ Bugun yangi:             <b>+{u['new_today']}</b>\n"
        f"├ Bu hafta yangi:          <b>+{u['new_week']}</b>\n"
        f"├ Buyurtma berganlar:      <b>{u['with_orders']}</b>\n"
        f"└ Hali xarid qilmaganlar: <b>{u['no_orders']}</b>\n\n"
        f"{DIVIDER}\n"
        "📦 <b>Buyurtmalar:</b>\n"
        f"├ Jami:         <b>{o['total']:,}</b>\n"
        f"├ Bugun:        <b>{o['today_orders']}</b>  (+{o['today_revenue']:,} so'm)\n"
        f"├ Bajarilgan:   <b>{o['completed']}</b>\n"
        f"├ Jarayonda:    <b>{o['pending']}</b>\n"
        f"├ Bekor:        <b>{o['canceled']}</b>\n"
        f"└ Jami tushum:  <b>{o['total_revenue']:,} so'm</b>\n\n"
        f"{DIVIDER}\n"
        "💰 <b>Depozitlar:</b>\n"
        f"├ Kutayotgan:         <b>{d['pending_count']}</b>  ({d['pending_sum']:,} so'm)\n"
        f"├ Bugun tasdiqlangan: <b>{d['today_confirmed']:,} so'm</b>\n"
        f"└ Jami tasdiqlangan:  <b>{d['confirmed_sum']:,} so'm</b>\n\n"
        f"{DIVIDER}\n"
        f"👛 Foydalanuvchilar balansi: <b>{u['total_balance']:,} so'm</b>"
    )


def _users_text(u: dict) -> str:
    return (
        f"👥 <b>Foydalanuvchilar</b>\n\n"
        f"{DIVIDER}\n"
        f"Jami:                    <b>{u['total']:,}</b>\n"
        f"Bugun yangi:             <b>+{u['new_today']}</b>\n"
        f"Bu hafta yangi:          <b>+{u['new_week']}</b>\n"
        f"Buyurtma berganlar:      <b>{u['with_orders']}</b>\n"
        f"Hali xarid qilmaganlar: <b>{u['no_orders']}</b>\n"
        f"Umumiy balans:           <b>{u['total_balance']:,} so'm</b>\n"
        f"{DIVIDER}"
    )


def _top_text(users: list) -> str:
    MEDALS = ["🥇", "🥈", "🥉"]
    lines  = [f"🏆 <b>Top 10 — eng ko'p xarid:</b>\n", DIVIDER]
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
    lines = [f"⏳ <b>Kutayotgan: {len(deposits)} ta</b>\n", DIVIDER]
    for d in deposits[:15]:
        ts = time.strftime("%d.%m %H:%M", time.localtime(d.get("created_at", 0)))
        lines.append(
            f"• <code>#{d['id']}</code>  {d.get('full_name', '?')}\n"
            f"  💰 {d['amount']:,} so'm  •  {ts}"
        )
    if len(deposits) > 15:
        lines.append(f"\n... va yana <b>{len(deposits) - 15}</b> ta")
    return "\n".join(lines)