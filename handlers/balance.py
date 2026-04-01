import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_balance, create_deposit, confirm_deposit, reject_deposit, get_deposit_status
from keyboards.menus import balance_menu, back_to_main, admin_deposit_keyboard
from config import CARD_NUMBER, CARD_OWNER, MIN_DEPOSIT, MAX_DEPOSIT, ADMIN_ID, GROUP_ID

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811").lstrip("@")

router = Router()


class DepositState(StatesGroup):
    waiting_amount = State()
    waiting_check = State()


def admin_contact_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👨‍💼 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()


def cancel_deposit_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_deposit"))
    return builder.as_markup()


def confirm_action_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    """Tasdiqlashdan oldin ishonch so'rovi klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Ha, tasdiqlayman", callback_data=f"adm_confirm_yes_{deposit_id}"),
        InlineKeyboardButton(text="🔙 Yo'q, orqaga", callback_data=f"adm_back_{deposit_id}")
    )
    return builder.as_markup()


def reject_action_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    """Rad etishdan oldin ishonch so'rovi klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Ha, rad etaman", callback_data=f"adm_reject_yes_{deposit_id}"),
        InlineKeyboardButton(text="🔙 Yo'q, orqaga", callback_data=f"adm_back_{deposit_id}")
    )
    return builder.as_markup()


# ── Foydalanuvchi handlerlari ──────────────────────────────────

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
        f"🌁 To'lovni amalga oshirgandan so'ng chekni yuboring.",
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
                chat_id=GROUP_ID,
                photo=file_id,
                caption=caption,
                reply_markup=admin_deposit_keyboard(deposit_id),
                parse_mode="HTML"
            )
            sent = True
        except Exception:
            pass

    if not sent:
        try:
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_id,
                caption=caption,
                reply_markup=admin_deposit_keyboard(deposit_id),
                parse_mode="HTML"
            )
        except Exception:
            pass


@router.message(DepositState.waiting_check)
async def process_check_wrong(message: Message):
    await message.answer(
        "📸 Iltimos, chekni <b>rasm sifatida</b> yuboring!\n\n"
        "📌 Faylni rasmga aylantirmang, to'g'ridan-to'g'ri rasm yuboring.",
        reply_markup=cancel_deposit_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(DepositState.waiting_check, F.data == "cancel_deposit")
async def cb_during_check_wait(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(
        "❌ Balans to'ldirish bekor qilindi.",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await call.answer()


# ── Admin handlerlari ──────────────────────────────────────────

@router.callback_query(F.data.startswith("adm_confirm_") & ~F.data.startswith("adm_confirm_yes_"))
async def admin_confirm_ask(call: CallbackQuery, bot: Bot):
    """Tasdiqlash tugmasi bosildi — avval ishonch so'raymiz"""
    deposit_id = int(call.data.split("_")[2])

    # Avval statusni tekshiramiz
    status = await get_deposit_status(deposit_id)
    if status is None:
        await call.answer("❌ Deposit topilmadi!", show_alert=True)
        return
    if status == "confirmed":
        await call.answer("ℹ️ Bu deposit allaqachon tasdiqlangan!", show_alert=True)
        return
    if status == "rejected":
        await call.answer(
            "⚠️ Bu deposit avval rad etilgan edi!\nBaribir tasdiqlashni xohlaysizmi?",
            show_alert=True
        )
        # Rad etilgan bo'lsa ham tasdiqlash imkonini beramiz (alohida tugma bilan)
        try:
            await call.message.edit_reply_markup(
                reply_markup=confirm_action_keyboard(deposit_id)
            )
        except Exception:
            pass
        return

    # Pending — ishonch so'raymiz
    try:
        await call.message.edit_reply_markup(
            reply_markup=confirm_action_keyboard(deposit_id)
        )
    except Exception:
        pass
    await call.answer("✅ Tasdiqlashni tasdiqlang 👆")


@router.callback_query(F.data.startswith("adm_confirm_yes_"))
async def admin_confirm_yes(call: CallbackQuery, bot: Bot):
    """Tasdiqlash tasdiqlandi"""
    deposit_id = int(call.data.split("_")[3])
    result = await confirm_deposit(deposit_id)

    if not result:
        await call.answer("❌ Deposit topilmadi yoki allaqachon qayta ishlangan!", show_alert=True)
        return

    user_id, amount = result

    try:
        old_caption = call.message.caption or ""
        new_caption = f"📌 Status: <b>TASDIQLANDI ✅</b>\nAdmin: @{call.from_user.username or call.from_user.id}\n\n{old_caption}"
        await call.message.edit_caption(new_caption, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
                 f"💰 <b>+{amount:,} so'm</b> balansingizga tushdi.\n\n"
                 f"Xaridlaringiz uchun rahmat! 🎉",
            reply_markup=back_to_main(),
            parse_mode="HTML"
        )
    except Exception:
        pass

    log_text = f"✅ Deposit #{deposit_id} tasdiqlandi — {amount:,} so'm | Admin: @{call.from_user.username or call.from_user.id}"
    try:
        await bot.send_message(GROUP_ID, log_text)
    except Exception:
        try:
            await bot.send_message(ADMIN_ID, log_text)
        except Exception:
            pass

    await call.answer("✅ Muvaffaqiyatli tasdiqlandi!")


@router.callback_query(F.data.startswith("adm_reject_") & ~F.data.startswith("adm_reject_yes_"))
async def admin_reject_ask(call: CallbackQuery, bot: Bot):
    """Rad etish tugmasi bosildi — avval ishonch so'raymiz"""
    deposit_id = int(call.data.split("_")[2])

    status = await get_deposit_status(deposit_id)
    if status is None:
        await call.answer("❌ Deposit topilmadi!", show_alert=True)
        return
    if status == "rejected":
        await call.answer("ℹ️ Bu deposit allaqachon rad etilgan!", show_alert=True)
        return
    if status == "confirmed":
        await call.answer("⚠️ Bu deposit allaqachon tasdiqlangan! Rad etib bo'lmaydi.", show_alert=True)
        return

    try:
        await call.message.edit_reply_markup(
            reply_markup=reject_action_keyboard(deposit_id)
        )
    except Exception:
        pass
    await call.answer("❌ Rad etishni tasdiqlang 👆")


@router.callback_query(F.data.startswith("adm_reject_yes_"))
async def admin_reject_yes(call: CallbackQuery, bot: Bot):
    """Rad etish tasdiqlandi"""
    deposit_id = int(call.data.split("_")[3])
    user_id = await reject_deposit(deposit_id)

    if not user_id:
        await call.answer("❌ Deposit topilmadi yoki allaqachon rad etilgan!", show_alert=True)
        return

    try:
        old_caption = call.message.caption or ""
        new_caption = f"📌 Status: <b>RAD ETILDI ❌</b>\nAdmin: @{call.from_user.username or call.from_user.id}\n\n{old_caption}"
        await call.message.edit_caption(new_caption, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    try:
        await bot.send_message(
            chat_id=user_id,
            text="❌ <b>To'lovingiz rad etildi.</b>\n\n"
                 "Sabab: chek noto'g'ri yoki summa mos kelmadi.\n"
                 "Muammo bo'lsa admin bilan bog'laning:",
            reply_markup=admin_contact_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        pass

    log_text = f"❌ Deposit #{deposit_id} rad etildi | Admin: @{call.from_user.username or call.from_user.id}"
    try:
        await bot.send_message(GROUP_ID, log_text)
    except Exception:
        try:
            await bot.send_message(ADMIN_ID, log_text)
        except Exception:
            pass

    await call.answer("❌ Rad etildi!")


@router.callback_query(F.data.startswith("adm_back_"))
async def admin_back(call: CallbackQuery):
    """Ishonch so'rovidan orqaga — asl klaviaturani qaytaramiz"""
    deposit_id = int(call.data.split("_")[2])
    try:
        await call.message.edit_reply_markup(
            reply_markup=admin_deposit_keyboard(deposit_id)
        )
    except Exception:
        pass
    await call.answer("🔙 Bekor qilindi")