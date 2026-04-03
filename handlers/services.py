from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from smm_api import (
    get_platform_names, get_section_names, get_section_services,
    find_service, calc_price_uzs, price_per_1000_uzs, place_order,
    get_markup, cost_price_uzs_per_item
)
from database import get_balance, deduct_balance, create_order, get_user_discount
import os

router = Router()


class OrderState(StatesGroup):
    waiting_quantity = State()
    waiting_link = State()


# ── Klaviaturalar (2 qatordan) ────────────────────────────────

def platforms_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    names = get_platform_names()
    # 2 tadan qator
    for i in range(0, len(names), 2):
        row = names[i:i+2]
        buttons = [
            InlineKeyboardButton(text=n, callback_data=f"plat_{n}")
            for n in row
        ]
        builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    return builder.as_markup()


def sections_keyboard(platform: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    sections = get_section_names(platform)
    for i in range(0, len(sections), 2):
        row = sections[i:i+2]
        buttons = [
            InlineKeyboardButton(text=s, callback_data=f"sec_{platform}|||{s}")
            for s in row
        ]
        builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="services"))
    return builder.as_markup()


def services_keyboard(platform: str, section: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in get_section_services(platform, section):
        markup = get_markup(s)
        p1000 = price_per_1000_uzs(s["rate"], markup)
        refill_badge = " ♻️" if s.get("refill") else ""
        builder.row(InlineKeyboardButton(
            text=f"{s['name']}{refill_badge} — {p1000:,} so'm/1000",
            callback_data=f"svc_{s['service']}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"plat_{platform}"))
    return builder.as_markup()


def order_confirm_keyboard(service_id: int, quantity: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_order_{service_id}_{quantity}"),
        InlineKeyboardButton(text="❌ Bekor", callback_data="services")
    )
    return builder.as_markup()


def back_to_main() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()


def _svc_card(svc: dict, markup: float) -> str:
    """Xizmat kartasi matni"""
    p1000 = price_per_1000_uzs(svc["rate"], markup)
    refill_line = "\n♻️ <b>Refill kafolatli</b>" if svc.get("refill") else ""
    bonus_line = f"\n🎁 <b>Bonus:</b> {svc['bonus']}" if svc.get("bonus") else ""
    return (
        f"<b>{svc['name']}</b>{refill_line}\n\n"
        f"📝 {svc.get('description', '')}{bonus_line}\n\n"
        f"📊 Min: <b>{svc['min']:,}</b> | Max: <b>{svc['max']:,}</b>\n"
        f"💰 Narx: <b>{p1000:,} so'm / 1 000 ta</b>\n\n"
        f"✏️ Nechta buyurtma bermoqchisiz?"
    )


# ── Handlerlar ─────────────────────────────────────────────────

@router.callback_query(F.data == "services")
async def cb_services(call: CallbackQuery):
    await call.message.edit_text(
        "🛍 <b>Xizmatlar</b>\n\nPlatformani tanlang:",
        reply_markup=platforms_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("plat_"))
async def cb_platform(call: CallbackQuery):
    platform = call.data[5:]
    await call.message.edit_text(
        f"<b>{platform} xizmatlari</b>\n\nBo'limni tanlang:",
        reply_markup=sections_keyboard(platform),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("sec_"))
async def cb_section(call: CallbackQuery):
    parts = call.data[4:].split("|||", 1)
    platform, section = parts[0], parts[1]
    await call.message.edit_text(
        f"<b>{platform} — {section}</b>\n\nXizmatni tanlang:",
        reply_markup=services_keyboard(platform, section),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("svc_"))
async def cb_service_detail(call: CallbackQuery, state: FSMContext):
    try:
        service_id = int(call.data.split("_")[1])
    except (IndexError, ValueError):
        await call.answer("❌ Xatolik!", show_alert=True)
        return

    svc = find_service(service_id)
    if not svc:
        await call.answer("❌ Xizmat topilmadi!", show_alert=True)
        return

    # Foydalanuvchining individual discountini tekshir
    discount = await get_user_discount(call.from_user.id)
    markup = get_markup(svc)

    # Discount — tan narxiga qarab hisoblanadi
    # 0%: oddiy markup
    # >0%: markup kamayadi (lekin hech qachon tan narxidan past emas)
    # <0%: markup oshadi (extra qimmatlashtirish)
    if discount != 0:
        cost = cost_price_uzs_per_item(svc["rate"]) * 1000  # per 1000
        base_price = price_per_1000_uzs(svc["rate"], markup)
        profit = base_price - cost
        adjusted_profit = profit * (1 - discount / 100)
        effective_price = max(cost, cost + adjusted_profit)
        # effective markupni qayta hisoblash
        if cost > 0:
            markup = max(0, (effective_price / cost - 1) * 100)

    await state.update_data(
        service_id=service_id,
        service_name=svc["name"],
        platform=svc.get("platform", ""),
        min_q=svc["min"],
        max_q=svc["max"],
        rate=svc["rate"],
        markup=markup,
    )
    await state.set_state(OrderState.waiting_quantity)

    await call.message.edit_text(
        _svc_card(svc, markup),
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
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

    if not (min_q <= quantity <= max_q):
        await message.answer(
            f"❌ Miqdor <b>{min_q:,}</b> — <b>{max_q:,}</b> oralig'ida bo'lishi kerak!",
            parse_mode="HTML"
        )
        return

    await state.update_data(quantity=quantity)
    await state.set_state(OrderState.waiting_link)
    await message.answer(
        "🔗 Link yuboring:\n\n"
        "📌 Telegram: kanal yoki post linki\n"
        "📌 Instagram / TikTok / YouTube / Facebook: post yoki profil linki"
    )


@router.message(OrderState.waiting_link)
async def process_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not (link.startswith("http") or link.startswith("@") or link.startswith("t.me")):
        await message.answer("❌ To'g'ri link kiriting! (https://... yoki @username)")
        return

    data = await state.get_data()
    markup = data.get("markup")
    total_price = calc_price_uzs(data["rate"], data["quantity"], markup)
    balance = await get_balance(message.from_user.id)

    await state.update_data(link=link, total_price=total_price)

    enough = balance >= total_price
    discount_line = ""
    if data.get("markup") is not None:
        discount = await get_user_discount(message.from_user.id)
        if discount != 0:
            sign = "-" if discount > 0 else "+"
            discount_line = f"\n🏷 Chegirma: <b>{sign}{abs(discount):.0f}%</b>"

    await message.answer(
        f"📦 <b>Buyurtma ma'lumotlari:</b>\n\n"
        f"🏷 Xizmat: <b>{data['service_name']}</b>\n"
        f"🔢 Miqdor: <b>{data['quantity']:,}</b>\n"
        f"🔗 Link: <code>{link}</code>\n"
        f"💰 Narx: <b>{total_price:,} so'm</b>{discount_line}\n"
        f"💳 Balans: <b>{balance:,.0f} so'm</b>\n\n"
        + ("✅ Balansingiz yetarli" if enough else
           f"❌ Balansingiz yetarli emas!\n💡 Kerak: {total_price:,} | Bor: {balance:,}"),
        reply_markup=(
            order_confirm_keyboard(data["service_id"], data["quantity"])
            if enough else back_to_main()
        ),
        parse_mode="HTML"
    )
    if not enough:
        await state.clear()


@router.callback_query(F.data.startswith("confirm_order_"))
async def cb_confirm_order(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    service_id = data.get("service_id")
    service_name = data.get("service_name")
    platform = data.get("platform", "")
    quantity = data.get("quantity")
    link = data.get("link")
    total_price = data.get("total_price")

    if not all([service_id, quantity, link, total_price]):
        await call.answer("❌ Ma'lumot topilmadi. Qaytadan urinib ko'ring.", show_alert=True)
        await state.clear()
        return

    if not await deduct_balance(call.from_user.id, total_price):
        await call.answer("❌ Balansingiz yetarli emas!", show_alert=True)
        await state.clear()
        return

    result = await place_order(service_id, link, quantity)
    smm_order_id = result.get("order")

    if not smm_order_id:
        await deduct_balance(call.from_user.id, -total_price)
        admin_username = os.getenv("ADMIN_USERNAME", "your_admin_username")
        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(
            text="🔄 Qayta urinib ko'rish",
            callback_data=f"retry_order_{service_id}_{quantity}"
        ))
        b.row(InlineKeyboardButton(
            text="👨‍💼 Adminga murojaat",
            url=f"https://t.me/{admin_username}"
        ))
        b.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
        await call.message.edit_text(
            f"❌ <b>Buyurtma berishda xatolik!</b>\n\n"
            f"💰 Pulingiz qaytarildi: <b>{total_price:,} so'm</b>\n\n"
            f"Qayta urinib ko'ring yoki admin bilan bog'laning 👇",
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

    # Referal foizi
    from database import get_referrer, add_referral_earning
    from config import REFERRAL_PERCENT
    referrer_id = await get_referrer(call.from_user.id)
    if referrer_id:
        percent_amount = round(total_price * REFERRAL_PERCENT / 100)
        await add_referral_earning(
            referrer_id, call.from_user.id, percent_amount, total_price, "percent"
        )
        user = call.from_user
        name = f"@{user.username}" if user.username else user.full_name
        try:
            await bot.send_message(
                referrer_id,
                f"💰 <b>Referal daromad!</b>\n\n"
                f"👤 {name} buyurtma berdi\n"
                f"➕ <b>+{percent_amount:,} so'm</b> ({REFERRAL_PERCENT:.0f}%) balansingizga tushdi!",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await state.clear()
    await call.message.edit_text(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"🔖 ID: <code>#{smm_order_id}</code>\n"
        f"🏷 Xizmat: <b>{service_name}</b>\n"
        f"🔢 Miqdor: <b>{quantity:,}</b>\n"
        f"💰 To'langan: <b>{total_price:,} so'm</b>\n\n"
        f"⏳ Bajarilmoqda... 'Buyurtmalarim' dan holat kuzating.",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("retry_order_"))
async def cb_retry_order(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    try:
        service_id = int(parts[2])
        quantity = int(parts[3])
    except (IndexError, ValueError):
        await call.answer("❌ Xatolik!", show_alert=True)
        return

    svc = find_service(service_id)
    if not svc:
        await call.answer("❌ Xizmat topilmadi!", show_alert=True)
        return

    discount = await get_user_discount(call.from_user.id)
    markup = get_markup(svc)
    total_price = calc_price_uzs(svc["rate"], quantity, markup)

    await state.update_data(
        service_id=service_id,
        service_name=svc["name"],
        platform=svc.get("platform", ""),
        min_q=svc["min"],
        max_q=svc["max"],
        rate=svc["rate"],
        markup=markup,
        quantity=quantity,
        total_price=total_price,
    )
    await state.set_state(OrderState.waiting_link)
    await call.message.edit_text(
        f"🔄 <b>Qayta buyurtma</b>\n\n"
        f"🏷 Xizmat: <b>{svc['name']}</b>\n"
        f"🔢 Miqdor: <b>{quantity:,}</b>\n"
        f"💰 Narx: <b>{total_price:,} so'm</b>\n\n"
        f"🔗 Linkni qayta kiriting:",
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await call.answer()