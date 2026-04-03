import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (
    get_balance, create_deposit, confirm_deposit, reject_deposit,
    get_deposit_status, get_pending_deposits, add_referral_earning
)
from keyboards.menus import admin_deposit_keyboard, back_to_main
from config import CARD_NUMBER, CARD_OWNER, MIN_DEPOSIT, MAX_DEPOSIT, ADMIN_ID, GROUP_ID

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811").lstrip("@")
DEPOSIT_BONUS = int(os.getenv("DEPOSIT_BONUS", "500"))  # Balans to'ldirganda referalga bonus

router = Router()


class DepositState(StatesGroup):
    waiting_amount = State()
    waiting_check = State()


class RejectState(StatesGroup):
    waiting_reason = State()


def balance_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Balansni to'ldirish", callback_data="deposit"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    return builder.as_markup()


def cancel_deposit_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_deposit"))
    return builder.as_markup()


def admin_contact_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👨‍💼 Admin bilan bog'lanish",
        url=f"https://t.me/{ADMIN_USERNAME}"
    ))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()


def confirm_action_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Ha, tasdiqlayman", callback_data=f"adm_confirm_yes_{deposit_id}"),
        InlineKeyboardButton(text="🔙 Yo'q", callback_data=f"adm_back_{deposit_id}")
    )
    return builder.as_markup()


def reject_ask_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    """Rad etish — sabab yozasizmi?"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Ha, sabab yozaman", callback_data=f"adm_reject_write_{deposit_id}"),
        InlineKeyboardButton(text="❌ Yo'q, shunchaki rad", callback_data=f"adm_reject_yes_{deposit_id}_")
    )
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"adm_back_{deposit_id}"))
    return builder.as_markup()


# ── Foydalanuvchi: balans ko'rish ─────────────────────────────

@router.callback_query(F.data == "balance")
async def cb_balance(call: CallbackQuery):
    bal = await get_balance(call.from_user.id)
    await call.message.edit_text(
        f"💰 <b>Balansingiz:</b> {bal:,} so'm\n\n"
        f"Balansni to'ldirish uchun quyidagi tugmani bosing.",
        reply_markup=balance_menu(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "deposit")
async def cb_deposit(call: CallbackQuery, state: FSMContext):
    await state.set_state(DepositState.waiting_amount)
    await call.message.edit_text(
        f"➕ <b>Balansni to'ldirish</b>\n\n"
        f"To'ldirmoqchi bo'lgan summani kiriting:\n"
        f"📌 Min: <b>{MIN_DEPOSIT:,}</b> so'm\n"
        f"📌 Max: <b>{MAX_DEPOSIT:,}</b> so'm",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await call.answer()


@router.message(DepositState.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    amount = int(text)
    if amount < MIN_DEPOSIT or amount > MAX_DEPOSIT:
        await message.answer(
            f"❌ Summa {MIN_DEPOSIT:,} — {MAX_DEPOSIT:,} so'm oralig'ida bo'lishi kerak!"
        )
        return
    await state.update_data(amount=amount)
    await state.set_state(DepositState.waiting_check)
    await message.answer(
        f"💳 <b>Quyidagi kartaga o'tkazing:</b>\n\n"
        f"🏦 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"👤 Egasi: <b>{CARD_OWNER}</b>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n\n"
        f"⏱ To'lov 5 daqiqa ichida ko'rib chiqiladi.\n"
        f"⚠️ Chekdagi summa to'g'ri bo'lishi shart.\n\n"
        f"🌁 To'lovni amalga oshirgach chekni yuboring:",
        reply_markup=cancel_deposit_keyboard(),
        parse_mode="HTML"
    )


@router.message(DepositState.waiting_check, F.photo)
async def process_check(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    amount = data.get("amount")
    file_id = message.photo[-1].file_id
    deposit_id = await create_deposit(message.from_user.id, amount, file_id)
    await state.clear()

    await message.answer(
        f"✅ Chek qabul qilindi!\n\n"
        f"💰 <b>{amount:,} so'm</b>\n"
        f"⏱ 5 daqiqa ichida ko'rib chiqiladi.",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )

    user = message.from_user
    caption = (
        f"📥 <b>Yangi to'ldirish so'rovi:</b>\n\n"
        f"👤 <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n"
        f"🔖 Deposit ID: <code>{deposit_id}</code>"
    )

    sent = False
    if GROUP_ID:
        try:
            await bot.send_photo(
                chat_id=GROUP_ID, photo=file_id, caption=caption,
                reply_markup=admin_deposit_keyboard(deposit_id), parse_mode="HTML"
            )
            sent = True
        except Exception:
            pass

    if not sent:
        try:
            await bot.send_photo(
                chat_id=ADMIN_ID, photo=file_id, caption=caption,
                reply_markup=admin_deposit_keyboard(deposit_id), parse_mode="HTML"
            )
        except Exception:
            pass


@router.message(DepositState.waiting_check)
async def process_check_wrong(message: Message):
    await message.answer(
        "📸 Iltimos, chekni <b>rasm sifatida</b> yuboring!",
        reply_markup=cancel_deposit_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(DepositState.waiting_check, F.data == "cancel_deposit")
async def cb_cancel_deposit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("❌ Balans to'ldirish bekor qilindi.", reply_markup=back_to_main())
    await call.answer()


# ── Admin: tasdiqlash ─────────────────────────────────────────

@router.callback_query(F.data.startswith("adm_confirm_") & ~F.data.startswith("adm_confirm_yes_"))
async def admin_confirm_ask(call: CallbackQuery):
    deposit_id = int(call.data.split("_")[2])
    status = await get_deposit_status(deposit_id)
    if status is None:
        await call.answer("❌ Deposit topilmadi!", show_alert=True)
        return
    if status == "confirmed":
        await call.answer("ℹ️ Allaqachon tasdiqlangan!", show_alert=True)
        return
    if status == "rejected":
        await call.answer("⚠️ Avval rad etilgan, tasdiqlayapsizmi?", show_alert=True)

    try:
        await call.message.edit_reply_markup(reply_markup=confirm_action_keyboard(deposit_id))
    except Exception:
        pass
    await call.answer("Tasdiqlashni tasdiqlang 👆")


@router.callback_query(F.data.startswith("adm_confirm_yes_"))
async def admin_confirm_yes(call: CallbackQuery, bot: Bot):
    deposit_id = int(call.data.split("_")[3])
    result = await confirm_deposit(deposit_id)

    if not result:
        await call.answer("❌ Topilmadi yoki allaqachon qayta ishlangan!", show_alert=True)
        return

    user_id, amount, referrer_id = result

    # Eski caption yangilash
    try:
        old = call.message.caption or ""
        new_cap = f"✅ <b>TASDIQLANDI</b>\nAdmin: @{call.from_user.username or call.from_user.id}\n\n{old}"
        await call.message.edit_caption(new_cap, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    # Foydalanuvchiga xabar
    try:
        await bot.send_message(
            user_id,
            f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            f"💰 <b>+{amount:,} so'm</b> balansingizga tushdi.\n\nXaridlaringiz uchun rahmat! 🎉",
            reply_markup=back_to_main(), parse_mode="HTML"
        )
    except Exception:
        pass

    # Referal egasiga deposit bonus (500 so'm)
    if referrer_id:
        try:
            await add_referral_earning(referrer_id, user_id, DEPOSIT_BONUS, amount, "deposit_bonus")
            await bot.send_message(
                referrer_id,
                f"🎉 <b>Referal deposit bonusi!</b>\n\n"
                f"Do'stingiz balanasini to'ldirdi!\n"
                f"➕ <b>+{DEPOSIT_BONUS:,} so'm</b> balansingizga tushdi!",
                parse_mode="HTML"
            )
        except Exception:
            pass

    log_text = (
        f"✅ Deposit #{deposit_id} tasdiqlandi — {amount:,} so'm | "
        f"Admin: @{call.from_user.username or call.from_user.id}"
    )
    for chat_id in [GROUP_ID, ADMIN_ID]:
        if chat_id:
            try:
                await bot.send_message(chat_id, log_text)
                break
            except Exception:
                continue

    await call.answer("✅ Muvaffaqiyatli tasdiqlandi!")


# ── Admin: rad etish ──────────────────────────────────────────

@router.callback_query(F.data.startswith("adm_reject_") & ~F.data.startswith("adm_reject_yes_") & ~F.data.startswith("adm_reject_write_"))
async def admin_reject_ask(call: CallbackQuery):
    deposit_id = int(call.data.split("_")[2])
    status = await get_deposit_status(deposit_id)
    if status is None:
        await call.answer("❌ Topilmadi!", show_alert=True)
        return
    if status == "rejected":
        await call.answer("ℹ️ Allaqachon rad etilgan!", show_alert=True)
        return
    if status == "confirmed":
        await call.answer("⚠️ Tasdiqlangan! Rad etib bo'lmaydi.", show_alert=True)
        return

    try:
        await call.message.edit_reply_markup(reply_markup=reject_ask_keyboard(deposit_id))
    except Exception:
        pass
    await call.answer("Rad etish — sabab yozasizmi?")


@router.callback_query(F.data.startswith("adm_reject_write_"))
async def admin_reject_write(call: CallbackQuery, state: FSMContext):
    """Admin sabab yozmoqchi"""
    deposit_id = int(call.data.split("_")[3])
    await state.update_data(reject_deposit_id=deposit_id, reject_msg_id=call.message.message_id)
    await state.set_state(RejectState.waiting_reason)
    await call.message.answer(
        f"✏️ Deposit #{deposit_id} uchun rad etish sababini yozing:\n\n"
        f"(Yozmaslik uchun /skip yuboring)",
    )
    await call.answer()


@router.message(RejectState.waiting_reason)
async def process_reject_reason(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    deposit_id = data.get("reject_deposit_id")
    reason = None if message.text == "/skip" else message.text.strip()
    await state.clear()
    await _do_reject(bot, deposit_id, reason, message.from_user)
    await message.answer(f"❌ Deposit #{deposit_id} rad etildi.")


@router.callback_query(F.data.startswith("adm_reject_yes_"))
async def admin_reject_yes(call: CallbackQuery, bot: Bot):
    """Sabab yozmasdan rad etish"""
    parts = call.data.split("_")
    deposit_id = int(parts[3])
    reason = parts[4] if len(parts) > 4 and parts[4] else None
    await _do_reject(bot, deposit_id, reason, call.from_user)

    try:
        old = call.message.caption or ""
        new_cap = f"❌ <b>RAD ETILDI</b>\nAdmin: @{call.from_user.username or call.from_user.id}\n\n{old}"
        await call.message.edit_caption(new_cap, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await call.answer("❌ Rad etildi!")


async def _do_reject(bot: Bot, deposit_id: int, reason: str | None, admin_user):
    user_id = await reject_deposit(deposit_id, reason)
    if not user_id:
        return

    reason_line = f"\n\n📝 Sabab: {reason}" if reason else ""
    try:
        await bot.send_message(
            user_id,
            f"❌ <b>To'lovingiz rad etildi.</b>{reason_line}\n\n"
            f"Muammo bo'lsa admin bilan bog'laning:",
            reply_markup=admin_contact_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        pass

    log_text = (
        f"❌ Deposit #{deposit_id} rad etildi"
        + (f" | Sabab: {reason}" if reason else "")
        + f" | Admin: @{admin_user.username or admin_user.id}"
    )
    for chat_id in [GROUP_ID, ADMIN_ID]:
        if chat_id:
            try:
                await bot.send_message(chat_id, log_text)
                break
            except Exception:
                continue


@router.callback_query(F.data.startswith("adm_back_"))
async def admin_back(call: CallbackQuery):
    deposit_id = int(call.data.split("_")[2])
    try:
        await call.message.edit_reply_markup(reply_markup=admin_deposit_keyboard(deposit_id))
    except Exception:
        pass
    await call.answer("🔙 Bekor qilindi")