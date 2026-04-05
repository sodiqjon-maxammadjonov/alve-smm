"""
handlers/balance.py — Zendor SMM Bot
Balans to'ldirish, depozit tasdiqlash/rad etish.
"""

import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    get_balance, create_deposit, confirm_deposit,
    reject_deposit, get_deposit_status, get_pending_deposits,
    add_referral_earning,
)
from keyboards.menus import (
    admin_deposit_keyboard, confirm_action_keyboard,
    reject_ask_keyboard, cancel_deposit_keyboard,
    admin_contact_keyboard, back_to_main,
)
from config import (
    CARD_NUMBER, CARD_OWNER, MIN_DEPOSIT, MAX_DEPOSIT,
    ADMIN_ID, GROUP_ID, DEPOSIT_BONUS,
)
from core.constants import DIVIDER

router = Router()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")


# ── FSM ───────────────────────────────────────────────────────

class DepositState(StatesGroup):
    waiting_amount = State()
    waiting_check  = State()


class RejectState(StatesGroup):
    waiting_reason = State()


# ── Matnlar ───────────────────────────────────────────────────

def _card_text(amount: int) -> str:
    return (
        f"💳 <b>To'lov ma'lumotlari</b>\n\n"
        f"{DIVIDER}\n"
        f"🏦 Karta raqami:\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"👤 Egasi: <b>{CARD_OWNER}</b>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n"
        f"{DIVIDER}\n\n"
        "📌 <b>Muhim eslatmalar:</b>\n"
        "├ Chekdagi summa to'g'ri bo'lishi shart\n"
        "├ To'lov 5 daqiqa ichida ko'rib chiqiladi\n"
        "└ Faqat UzCard / Humo orqali\n\n"
        "📸 <b>To'lovdan so'ng chekni yuboring:</b>"
    )


# ── Foydalanuvchi: Balans to'ldirish ─────────────────────────

@router.callback_query(F.data == "deposit")
async def cb_deposit(call: CallbackQuery, state: FSMContext):
    await state.set_state(DepositState.waiting_amount)
    await call.message.edit_text(
        f"➕ <b>Balans to'ldirish</b>\n\n"
        f"{DIVIDER}\n"
        "To'ldirmoqchi bo'lgan summani kiriting:\n\n"
        f"📌 Minimal: <b>{MIN_DEPOSIT:,} so'm</b>\n"
        f"📌 Maksimal: <b>{MAX_DEPOSIT:,} so'm</b>\n"
        f"{DIVIDER}",
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer()


@router.message(DepositState.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("❌ Faqat <b>raqam</b> kiriting!", parse_mode="HTML")
        return
    amount = int(text)
    if not (MIN_DEPOSIT <= amount <= MAX_DEPOSIT):
        await message.answer(
            f"❌ Summa <b>{MIN_DEPOSIT:,}</b> — <b>{MAX_DEPOSIT:,}</b> so'm oralig'ida bo'lishi kerak!",
            parse_mode="HTML",
        )
        return
    await state.update_data(amount=amount)
    await state.set_state(DepositState.waiting_check)
    await message.answer(
        _card_text(amount),
        reply_markup=cancel_deposit_keyboard(),
        parse_mode="HTML",
    )


@router.message(DepositState.waiting_check, F.photo)
async def process_check(message: Message, state: FSMContext, bot: Bot):
    data       = await state.get_data()
    amount     = data["amount"]
    file_id    = message.photo[-1].file_id
    deposit_id = await create_deposit(message.from_user.id, amount, file_id)
    await state.clear()

    await message.answer(
        f"✅ <b>Chek qabul qilindi!</b>\n\n"
        f"{DIVIDER}\n"
        f"💰 Summa:  <b>{amount:,} so'm</b>\n"
        f"🔖 ID:     <code>#{deposit_id}</code>\n"
        f"⏳ Status: <b>Kutilmoqda</b>\n"
        f"{DIVIDER}\n\n"
        "✅ 5 daqiqa ichida ko'rib chiqiladi.",
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )

    user    = message.from_user
    caption = (
        f"📥 <b>Yangi depozit so'rovi</b>\n\n"
        f"{DIVIDER}\n"
        f"👤 <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n"
        f"🔖 Deposit ID: <code>#{deposit_id}</code>\n"
        f"{DIVIDER}"
    )

    sent = False
    for chat_id in [GROUP_ID, ADMIN_ID]:
        if chat_id and not sent:
            try:
                await bot.send_photo(
                    chat_id=chat_id, photo=file_id, caption=caption,
                    reply_markup=admin_deposit_keyboard(deposit_id),
                    parse_mode="HTML",
                )
                sent = True
            except Exception:
                pass


@router.message(DepositState.waiting_check)
async def process_check_wrong(message: Message):
    await message.answer(
        "📸 Iltimos, chekni <b>rasm sifatida</b> yuboring!\n\nSkreenshot olib yuboring.",
        reply_markup=cancel_deposit_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(DepositState.waiting_check, F.data == "cancel_deposit")
async def cb_cancel_deposit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ <b>Balans to'ldirish bekor qilindi.</b>",
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer()


# ── Admin: Tasdiqlash ─────────────────────────────────────────

@router.callback_query(
    F.data.startswith("adm_confirm_") & ~F.data.startswith("adm_confirm_yes_")
)
async def admin_confirm_ask(call: CallbackQuery):
    deposit_id = int(call.data.split("_")[2])
    status     = await get_deposit_status(deposit_id)
    if status is None:
        await call.answer("❌ Deposit topilmadi!", show_alert=True); return
    if status == "confirmed":
        await call.answer("ℹ️ Allaqachon tasdiqlangan!", show_alert=True); return
    if status == "rejected":
        await call.answer("⚠️ Avval rad etilgan!", show_alert=True); return
    try:
        await call.message.edit_reply_markup(reply_markup=confirm_action_keyboard(deposit_id))
    except Exception:
        pass
    await call.answer("Tasdiqlashni tasdiqlang 👆")


@router.callback_query(F.data.startswith("adm_confirm_yes_"))
async def admin_confirm_yes(call: CallbackQuery, bot: Bot):
    deposit_id = int(call.data.split("_")[3])
    result     = await confirm_deposit(deposit_id)

    if not result:
        await call.answer("❌ Topilmadi yoki allaqachon qayta ishlangan!", show_alert=True)
        return

    user_id, amount, referrer_id = result

    try:
        old = call.message.caption or ""
        await call.message.edit_caption(
            f"✅ <b>TASDIQLANDI</b>\n"
            f"Admin: @{call.from_user.username or call.from_user.id}\n\n{old}",
            reply_markup=None, parse_mode="HTML",
        )
    except Exception:
        pass

    try:
        await bot.send_message(
            user_id,
            f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            f"{DIVIDER}\n"
            f"💰 <b>+{amount:,} so'm</b> balansingizga tushdi!\n"
            f"{DIVIDER}\n\n"
            "🛍 Endi xizmatlardan foydalanishingiz mumkin!",
            reply_markup=back_to_main(), parse_mode="HTML",
        )
    except Exception:
        pass

    if referrer_id:
        try:
            await add_referral_earning(
                referrer_id, user_id, DEPOSIT_BONUS, amount, "deposit_bonus"
            )
            await bot.send_message(
                referrer_id,
                f"🎉 <b>Referal deposit bonusi!</b>\n\n"
                f"Do'stingiz balansini to'ldirdi!\n"
                f"➕ <b>+{DEPOSIT_BONUS:,} so'm</b> balansingizga tushdi!",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await call.answer("✅ Muvaffaqiyatli tasdiqlandi!")


# ── Admin: Rad etish ──────────────────────────────────────────

@router.callback_query(
    F.data.startswith("adm_reject_") &
    ~F.data.startswith("adm_reject_yes_") &
    ~F.data.startswith("adm_reject_write_")
)
async def admin_reject_ask(call: CallbackQuery):
    deposit_id = int(call.data.split("_")[2])
    status     = await get_deposit_status(deposit_id)
    if status is None:
        await call.answer("❌ Topilmadi!", show_alert=True); return
    if status == "rejected":
        await call.answer("ℹ️ Allaqachon rad etilgan!", show_alert=True); return
    if status == "confirmed":
        await call.answer("⚠️ Tasdiqlangan — rad etib bo'lmaydi.", show_alert=True); return
    try:
        await call.message.edit_reply_markup(reply_markup=reject_ask_keyboard(deposit_id))
    except Exception:
        pass
    await call.answer()


@router.callback_query(F.data.startswith("adm_reject_write_"))
async def admin_reject_write(call: CallbackQuery, state: FSMContext):
    deposit_id = int(call.data.split("_")[3])
    await state.update_data(reject_deposit_id=deposit_id)
    await state.set_state(RejectState.waiting_reason)
    await call.message.answer(
        f"✏️ Deposit <code>#{deposit_id}</code> uchun rad etish sababini yozing:\n\n"
        "<i>O'tkazib yuborish uchun: /skip</i>",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(RejectState.waiting_reason)
async def process_reject_reason(message: Message, state: FSMContext, bot: Bot):
    data       = await state.get_data()
    deposit_id = data.get("reject_deposit_id")
    reason     = None if message.text == "/skip" else message.text.strip()
    await state.clear()
    await _do_reject(bot, deposit_id, reason, message.from_user)
    await message.answer(
        f"❌ Deposit <code>#{deposit_id}</code> rad etildi.",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_reject_yes_"))
async def admin_reject_yes(call: CallbackQuery, bot: Bot):
    parts      = call.data.split("_")
    deposit_id = int(parts[3])
    reason     = parts[4] if len(parts) > 4 and parts[4] else None
    await _do_reject(bot, deposit_id, reason, call.from_user)
    try:
        old = call.message.caption or ""
        await call.message.edit_caption(
            f"❌ <b>RAD ETILDI</b>\n"
            f"Admin: @{call.from_user.username or call.from_user.id}\n\n{old}",
            reply_markup=None, parse_mode="HTML",
        )
    except Exception:
        pass
    await call.answer("❌ Rad etildi!")


async def _do_reject(bot: Bot, deposit_id: int, reason: str | None, admin_user) -> None:
    user_id = await reject_deposit(deposit_id, reason)
    if not user_id:
        return

    reason_line = f"\n\n📝 Sabab: {reason}" if reason else ""
    try:
        await bot.send_message(
            user_id,
            f"❌ <b>To'lovingiz rad etildi.</b>{reason_line}\n\n"
            "Muammo bo'lsa admin bilan bog'laning 👇",
            reply_markup=admin_contact_keyboard(ADMIN_USERNAME),
            parse_mode="HTML",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm_back_"))
async def admin_back(call: CallbackQuery):
    deposit_id = int(call.data.split("_")[2])
    try:
        await call.message.edit_reply_markup(reply_markup=admin_deposit_keyboard(deposit_id))
    except Exception:
        pass
    await call.answer("↩️ Bekor qilindi")
