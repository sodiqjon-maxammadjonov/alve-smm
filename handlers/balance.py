from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_balance, create_deposit, confirm_deposit, reject_deposit
from keyboards.menus import balance_menu, back_to_main, admin_deposit_keyboard
from config import CARD_NUMBER, CARD_OWNER, MIN_DEPOSIT, MAX_DEPOSIT, ADMIN_ID, GROUP_ID
import os
import logging

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")

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
    builder.row(InlineKeyboardButton(text="❌ Balans to'ldirishni bekor qilish", callback_data="cancel_deposit"))
    return builder.as_markup()

@router.callback_query(F.data == "balance")
async def cb_balance(call: CallbackQuery):
    bal = await get_balance(call.from_user.id)
    await call.message.edit_text(
        f"💰 <b>Balansingiz:</b> {bal:,.0f} so'm\n\n"
        f"Balansni to'ldirish uchun quyidagi tugmani bosing.",
        reply_markup=balance_menu(),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "deposit")
async def cb_deposit(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        f"➕ <b>Balansni to'ldirish</b>\n\n"
        f"To'ldirmoqchi bo'lgan summani kiriting:\n"
        f"📌 Min: <b>{MIN_DEPOSIT:,}</b> so'm\n"
        f"📌 Max: <b>{MAX_DEPOSIT:,}</b> so'm",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await state.set_state(DepositState.waiting_amount)
    await call.answer()

@router.message(DepositState.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    text = message.text.replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    amount = int(text)
    if amount < MIN_DEPOSIT or amount > MAX_DEPOSIT:
        await message.answer(f"❌ Summa {MIN_DEPOSIT:,} — {MAX_DEPOSIT:,} so'm oralig'ida bo'lishi kerak!")
        return

    await state.update_data(amount=amount)
    await message.answer(
        f"💳 <b>Quyidagi kartaga o'tkazing:</b>\n\n"
        f"🏦 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"👤 Egasi: <b>{CARD_OWNER}</b>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n\n"
        f"⏱ To'lov 5 daqiqa ichida ko'rib chiqiladi.\n"
        f"⚠️ Chekdagi summa to‘g‘ri bo‘lishi shart.\n\n"
        f"🌁 To‘lovni amalga oshirgandan so‘ng chekni yuboring.",
        parse_mode="HTML"
    )
    await state.set_state(DepositState.waiting_check)

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
        f"⏱ 5 daqiqa ichida ko‘rib chiqiladi.",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )

    user = message.from_user
    caption = (
        f"📥 <b>Yangi to‘ldirish:</b>\n\n"
        f"👤 <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n"
        f"🔖 Deposit ID: <code>{deposit_id}</code>"
    )

    try:
        await bot.send_photo(
            chat_id=GROUP_ID,
            photo=file_id,
            caption=caption,
            reply_markup=admin_deposit_keyboard(deposit_id),
            parse_mode="HTML"
        )
    except:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=caption,
            reply_markup=admin_deposit_keyboard(deposit_id),
            parse_mode="HTML"
        )

@router.message(DepositState.waiting_check)
async def process_check_wrong(message: Message):
    await message.answer(
        "📸 Iltimos, chekni rasm sifatida yuboring!",
        reply_markup=cancel_deposit_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(DepositState.waiting_check)
async def cb_during_check_wait(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if call.data == "cancel_deposit":
        await call.message.answer(
            "❌ Balans to‘ldirish bekor qilindi.",
            reply_markup=back_to_main(),
            parse_mode="HTML"
        )
        await call.answer()
        return
    await call.answer()

@router.callback_query(F.data.startswith("adm_confirm_"))
async def admin_confirm(call: CallbackQuery, bot: Bot):
    deposit_id = int(call.data.split("_")[2])
    result = await confirm_deposit(deposit_id)
    if not result:
        await call.answer("❌ Deposit topilmadi!", show_alert=True)
        return

    user_id, amount = result

    try:
        await call.message.edit_reply_markup(None)
        new_caption = (call.message.caption or "") + "\n\n✅ <b>TASDIQLANDI</b>"
        await call.message.edit_caption(new_caption, parse_mode="HTML")
    except:
        pass

    try:
        await bot.send_message(
            user_id,
            f"✅ To‘lov tasdiqlandi!\n\n+{amount:,.0f} so‘m balansingizga tushdi.",
            reply_markup=back_to_main(),
            parse_mode="HTML"
        )
    except:
        pass

    await call.answer("Tasdiqlandi!")

@router.callback_query(F.data.startswith("adm_reject_"))
async def admin_reject(call: CallbackQuery, bot: Bot):
    deposit_id = int(call.data.split("_")[2])
    user_id = await reject_deposit(deposit_id)
    if not user_id:
        await call.answer("❌ Deposit topilmadi!", show_alert=True)
        return

    try:
        await call.message.edit_reply_markup(None)
        new_caption = (call.message.caption or "") + "\n\n❌ <b>RAD ETILDI</b>"
        await call.message.edit_caption(new_caption, parse_mode="HTML")
    except:
        pass

    try:
        await bot.send_message(
            user_id,
            "❌ To‘lovingiz rad etildi.\n\nMuammo bo‘lsa admin bilan bog‘laning:",
            reply_markup=admin_contact_keyboard(),
            parse_mode="HTML"
        )
    except:
        pass

    await call.answer("Rad etildi!")