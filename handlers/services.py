from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from smm_api import (
    get_tg_section_names, get_ig_section_names,
    get_section_services, find_service,
    calc_order_price, price_per_1000_uzs, place_order
)
from database import get_balance, deduct_balance, create_order
from keyboards.menus import services_menu, order_confirm_keyboard, back_to_main

router = Router()

class OrderState(StatesGroup):
    waiting_quantity = State()
    waiting_link     = State()

# ── Klaviaturalar ──────────────────────────────────────────────

def tg_sections_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name in get_tg_section_names():
        builder.row(InlineKeyboardButton(
            text=name,
            callback_data=f"tgsec_{name}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="services"))
    return builder.as_markup()

def ig_sections_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name in get_ig_section_names():
        builder.row(InlineKeyboardButton(
            text=name,
            callback_data=f"igsec_{name}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="services"))
    return builder.as_markup()

def section_services_keyboard(platform: str, section: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    services = get_section_services(platform, section)
    back_cb = f"platform_{platform}"
    for s in services:
        p1000 = price_per_1000_uzs(s["rate"])
        builder.row(InlineKeyboardButton(
            text=f"{s['name']} — {p1000:,} so'm/1000",
            callback_data=f"svc_{s['service']}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=back_cb))
    return builder.as_markup()

# ── Handlerlar ─────────────────────────────────────────────────

@router.callback_query(F.data == "services")
async def cb_services(call: CallbackQuery):
    await call.message.edit_text(
        "🛍 <b>Hizmatlar</b>\n\nPlatformani tanlang:",
        reply_markup=services_menu(),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "platform_telegram")
async def cb_platform_telegram(call: CallbackQuery):
    await call.message.edit_text(
        "✈️ <b>Telegram hizmatlari</b>\n\nBo'limni tanlang:",
        reply_markup=tg_sections_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "platform_instagram")
async def cb_platform_instagram(call: CallbackQuery):
    await call.message.edit_text(
        "📸 <b>Instagram hizmatlari</b>\n\nBo'limni tanlang:",
        reply_markup=ig_sections_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data.startswith("tgsec_"))
async def cb_tg_section(call: CallbackQuery):
    section = call.data[6:]
    await call.message.edit_text(
        f"✈️ <b>Telegram — {section}</b>\n\nHizmatni tanlang:",
        reply_markup=section_services_keyboard("telegram", section),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data.startswith("igsec_"))
async def cb_ig_section(call: CallbackQuery):
    section = call.data[6:]
    await call.message.edit_text(
        f"📸 <b>Instagram — {section}</b>\n\nHizmatni tanlang:",
        reply_markup=section_services_keyboard("instagram", section),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data.startswith("svc_"))
async def cb_service_detail(call: CallbackQuery, state: FSMContext):
    service_id = int(call.data.split("_")[1])
    svc = find_service(service_id)
    if not svc:
        await call.answer("❌ Hizmat topilmadi!", show_alert=True)
        return

    rate   = svc["rate"]
    min_q  = svc["min"]
    max_q  = svc["max"]
    p1000  = price_per_1000_uzs(rate)

    await state.update_data(
        service_id=service_id,
        service_name=svc["name"],
        platform=svc["platform"],
        min_q=min_q,
        max_q=max_q,
        rate=rate
    )

    await call.message.edit_text(
        f"<b>{svc['name']}</b>\n\n"
        f"📝 {svc.get('description', '')}\n\n"
        f"📊 Minimal: <b>{min_q:,}</b>\n"
        f"📊 Maksimal: <b>{max_q:,}</b>\n"
        f"💰 Narx: <b>{p1000:,} so'm / 1 000 ta</b>\n\n"
        f"✏️ Nechta buyurtma bermoqchisiz? Raqam kiriting:",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_quantity)
    await call.answer()

@router.message(OrderState.waiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    text = message.text.replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    quantity = int(text)
    data = await state.get_data()
    min_q = data.get("min_q", 1)
    max_q = data.get("max_q", 99999)

    if quantity < min_q or quantity > max_q:
        await message.answer(
            f"❌ Miqdor <b>{min_q:,}</b> — <b>{max_q:,}</b> oralig'ida bo'lishi kerak!",
            parse_mode="HTML"
        )
        return

    await state.update_data(quantity=quantity)
    await message.answer(
        "🔗 Endi link yuboring:\n\n"
        "📌 Telegram uchun: kanal yoki post linki\n"
        "📌 Instagram uchun: post yoki profil linki"
    )
    await state.set_state(OrderState.waiting_link)

@router.message(OrderState.waiting_link)
async def process_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not (link.startswith("http") or link.startswith("@") or link.startswith("t.me")):
        await message.answer("❌ To'g'ri link kiriting! (https://... yoki @username)")
        return

    data        = await state.get_data()
    service_id  = data["service_id"]
    service_name = data["service_name"]
    quantity    = data["quantity"]
    rate        = data["rate"]
    platform    = data["platform"]

    total_price = calc_order_price(rate, quantity)
    balance     = await get_balance(message.from_user.id)

    await state.update_data(link=link, total_price=total_price)

    status = "✅ Balansingiz yetarli" if balance >= total_price else f"❌ Balansingiz yetarli emas! ({balance:,.0f} so'm bor)"

    await message.answer(
        f"📦 <b>Buyurtma ma'lumotlari:</b>\n\n"
        f"🏷 Hizmat: <b>{service_name}</b>\n"
        f"🔢 Miqdor: <b>{quantity:,}</b>\n"
        f"🔗 Link: <code>{link}</code>\n"
        f"💰 Narx: <b>{total_price:,} so'm</b>\n"
        f"💳 Balansingiz: <b>{balance:,.0f} so'm</b>\n\n"
        f"{status}",
        reply_markup=order_confirm_keyboard(service_id, quantity) if balance >= total_price else back_to_main(),
        parse_mode="HTML"
    )
    if balance < total_price:
        await state.clear()

@router.callback_query(F.data.startswith("confirm_order_"))
async def cb_confirm_order(call: CallbackQuery, state: FSMContext, bot: Bot):
    data         = await state.get_data()
    service_id   = data.get("service_id")
    service_name = data.get("service_name")
    platform     = data.get("platform")
    quantity     = data.get("quantity")
    link         = data.get("link")
    total_price  = data.get("total_price")

    if not all([service_id, quantity, link, total_price]):
        await call.answer("❌ Ma'lumot topilmadi. Qaytadan urinib ko'ring.", show_alert=True)
        await state.clear()
        return

    success = await deduct_balance(call.from_user.id, total_price)
    if not success:
        await call.answer("❌ Balansingiz yetarli emas!", show_alert=True)
        await state.clear()
        return

    result = await place_order(service_id, link, quantity)
    smm_order_id = result.get("order")

    if not smm_order_id:
        await deduct_balance(call.from_user.id, -total_price)
        import os
        admin_username = os.getenv("ADMIN_USERNAME", "your_admin_username")
        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(text="🔄 Qayta urinib ko'rish", callback_data=f"retry_order_{service_id}_{quantity}"))
        b.row(InlineKeyboardButton(text="👨‍💼 Adminga murojaat", url=f"https://t.me/{admin_username}"))
        b.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
        await call.message.edit_text(
            f"❌ <b>Buyurtma berishda xatolik yuz berdi!</b>\n\n"
            f"💰 Pulingiz qaytarildi: <b>{total_price:,} so'm</b>\n\n"
            f"🔁 Bir zumdan so'ng qayta urinib ko'ring.\n"
            f"Muammo davom etsa, admin bilan bog'laning 👇",
            reply_markup=b.as_markup(),
            parse_mode="HTML"
        )
        await call.answer()
        await state.clear()
        return

    await create_order(
        call.from_user.id, smm_order_id, service_id,
        service_name, platform, link, quantity, total_price
    )

    # Referal mexanikasi
    from database import get_referrer, is_first_order, was_bonus_given, mark_bonus_given, add_referral_earning
    from config import REFERRAL_PERCENT, REFERRAL_BONUS
    referrer_id = await get_referrer(call.from_user.id)
    if referrer_id:
        percent_amount = round(total_price * REFERRAL_PERCENT / 100)
        await add_referral_earning(referrer_id, call.from_user.id, percent_amount, total_price, "percent")
        try:
            await bot.send_message(
                referrer_id,
                f"💰 <b>Referal daromad!</b>\n\n"
                f"Do'stingiz buyurtma berdi va sizga <b>+{percent_amount:,} so'm</b> ({REFERRAL_PERCENT:.0f}%) balansga tushdi!",
                parse_mode="HTML"
            )
        except Exception:
            pass
        first_order = await is_first_order(call.from_user.id)
        bonus_given = await was_bonus_given(call.from_user.id)
        if first_order and not bonus_given:
            await mark_bonus_given(call.from_user.id)
            await add_referral_earning(referrer_id, call.from_user.id, REFERRAL_BONUS, total_price, "bonus")
            try:
                await bot.send_message(
                    referrer_id,
                    f"🎁 <b>Birinchi buyurtma bonusi!</b>\n\n"
                    f"Do'stingiz birinchi marta buyurtma berdi — sizga <b>+{REFERRAL_BONUS:,} so'm bonus</b> tushdi!",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    await state.clear()
    await call.message.edit_text(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"🔖 Buyurtma ID: <code>#{smm_order_id}</code>\n"
        f"🏷 Hizmat: <b>{service_name}</b>\n"
        f"🔢 Miqdor: <b>{quantity:,}</b>\n"
        f"💰 To'langan: <b>{total_price:,} so'm</b>\n\n"
        f"⏳ Bajarilmoqda... 'Buyurtmalarim' dan holat kuzating.",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data.startswith("retry_order_"))
async def cb_retry_order(call: CallbackQuery, state: FSMContext):
    parts     = call.data.split("_")
    service_id = int(parts[2])
    quantity   = int(parts[3])
    svc = find_service(service_id)
    if not svc:
        await call.answer("❌ Hizmat topilmadi!", show_alert=True)
        return
    rate        = svc["rate"]
    total_price = calc_order_price(rate, quantity)
    await state.update_data(
        service_id=service_id,
        service_name=svc["name"],
        platform=svc["platform"],
        min_q=svc["min"],
        max_q=svc["max"],
        rate=rate,
        quantity=quantity,
        total_price=total_price,
    )
    await call.message.edit_text(
        f"🔄 <b>Qayta buyurtma</b>\n\n"
        f"🏷 Hizmat: <b>{svc['name']}</b>\n"
        f"🔢 Miqdor: <b>{quantity:,}</b>\n"
        f"💰 Narx: <b>{total_price:,} so'm</b>\n\n"
        f"🔗 Linkni qayta kiriting:",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_link)
    await call.answer()