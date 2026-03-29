from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_balance, create_deposit, confirm_deposit, reject_deposit
from keyboards.menus import balance_menu, back_to_main, admin_deposit_keyboard
from config import CARD_NUMBER, CARD_OWNER, MIN_DEPOSIT, MAX_DEPOSIT, ADMIN_ID, GROUP_ID
import os

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "your_admin_username")

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
        await message.answer(
            f"❌ Summa {MIN_DEPOSIT:,} — {MAX_DEPOSIT:,} so'm oralig'ida bo'lishi kerak!"
        )
        return
    await state.update_data(amount=amount)
    await message.answer(
        f"💳 <b>Quyidagi kartaga o'tkazing:</b>\n\n"
        f"🏦 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"👤 Egasi: <b>{CARD_OWNER}</b>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n\n"
        f"⏱ To'lov <b>5 daqiqa</b> ichida ko'rib chiqiladi.\n"
        f"✅ Ma'lumotlar to'g'ri bo'lsa, to'lovingiz tasdiqlanib balansingizga tushadi.\n\n"
        f"⚠️ <b>Diqqat!</b> Chekdagi summa yuborgan summangiz bilan <b>bir xil</b> bo'lishi shart.\n"
        f"Aks holda to'lov qabul qilinmaydi.\n\n"
        f"✅ To'lovni amalga oshirgandan so'ng <b>chek (screenshot)</b>ni yuboring.",
        parse_mode="HTML"
    )
    await state.set_state(DepositState.waiting_check)

@router.message(DepositState.waiting_check, F.photo)
async def process_check(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    amount = data.get("amount", 0)
    file_id = message.photo[-1].file_id

    deposit_id = await create_deposit(message.from_user.id, amount, file_id)
    await state.clear()

    await message.answer(
        f"✅ <b>Chek qabul qilindi!</b>\n\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n"
        f"⏱ <b>5 daqiqa</b> ichida ko'rib chiqiladi.\n\n"
        f"Tasdiqlangandan so'ng balansingizga avtomatik tushadi.",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )

    user = message.from_user
    caption = (
        f"📥 <b>Yangi to'ldirish so'rovi</b>\n\n"
        f"👤 Foydalanuvchi: <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n"
        f"🔖 Deposit ID: <code>{deposit_id}</code>"
    )

    await bot.send_photo(
        chat_id=GROUP_ID,
        photo=file_id,
        caption=caption,
        reply_markup=admin_deposit_keyboard(deposit_id),
        parse_mode="HTML"
    )

@router.message(DepositState.waiting_check)
async def process_check_wrong(message: Message):
    await message.answer(
        "📸 Iltimos, to'lov chekini <b>rasm</b> sifatida yuboring!\n\n"
        "Yoki balans to'ldirishni bekor qilishingiz mumkin 👇",
        reply_markup=cancel_deposit_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(DepositState.waiting_check)
async def cb_during_check_wait(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if call.data == "cancel_deposit":
        await call.message.answer(
            "❌ <b>Balans to'ldirish bekor qilindi.</b>",
            reply_markup=back_to_main(),
            parse_mode="HTML"
        )
        await call.answer("Bekor qilindi")
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
    await call.message.edit_caption(
        call.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
        parse_mode="HTML",
        reply_markup=None
    )
    await bot.send_message(
        user_id,
        f"✅ <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"💰 <b>+{amount:,.0f} so'm</b> balansingizga tushdi.\n\n"
        f"Endi hizmatlardan bemalol foydalanishingiz mumkin. 🎉",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await call.answer("✅ Tasdiqlandi!")

@router.callback_query(F.data.startswith("adm_reject_"))
async def admin_reject(call: CallbackQuery, bot: Bot):
    deposit_id = int(call.data.split("_")[2])
    user_id = await reject_deposit(deposit_id)
    if not user_id:
        await call.answer("❌ Deposit topilmadi!", show_alert=True)
        return
    await call.message.edit_caption(
        call.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
        parse_mode="HTML",
        reply_markup=None
    )
    await bot.send_message(
        user_id,
        f"❌ <b>To'lovingiz qabul qilinmadi.</b>\n\n"
        f"Sabab: chekdagi summa yoki ma'lumotlar noto'g'ri bo'lishi mumkin.\n\n"
        f"Muammo bo'lsa admin bilan bog'laning 👇",
        reply_markup=admin_contact_keyboard(),
        parse_mode="HTML"
    )
    await call.answer("❌ Rad etildi!")