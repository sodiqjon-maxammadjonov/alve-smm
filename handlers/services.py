"""
handlers/services.py — Zendor SMM Bot
Xizmatlar, platformalar, bo'limlar, buyurtma berish jarayoni.
"""

import os
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.smm_api import (
    get_platform_names, get_section_names, get_section_services,
    find_service, find_platform_section,
    calc_price_uzs, price_per_1000_uzs, get_markup,
    cost_price_uzs_per_item, place_order, is_coming_soon,
)
from database import get_balance, deduct_balance, create_order, get_user_discount
from handlers.link_config import get_link_info, validate_link
from keyboards.menus import (
    platforms_keyboard, sections_keyboard, services_list_keyboard,
    order_confirm_keyboard, order_error_keyboard, back_to_main,
)
from core.constants import DIVIDER

router = Router()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")


# ── FSM holatlari ─────────────────────────────────────────────

class OrderState(StatesGroup):
    waiting_quantity = State()  # 1. Miqdor
    waiting_link     = State()  # 2. Link
    waiting_comments = State()  # 3. Custom Comments (ixtiyoriy)


# ── Yordamchi matnlar ─────────────────────────────────────────

def _service_detail_text(svc: dict, markup: float, discount: float = 0) -> str:
    p1000   = price_per_1000_uzs(svc["rate"], markup)
    refill  = "\n♻️ <b>Refill kafolatli</b>" if svc.get("refill") else ""
    disc_ln = f"\n🏷 Sizning chegirmangiz: <b>{discount:+.0f}%</b>" if discount != 0 else ""
    return (
        f"{DIVIDER}\n"
        f"📌 <b>{svc['name']}</b>{refill}\n"
        f"{DIVIDER}\n\n"
        f"📝 {svc.get('description', '—')}\n\n"
        f"📊 <b>Miqdor chegarasi:</b>\n"
        f"├ Minimal: <b>{svc['min']:,}</b>\n"
        f"└ Maksimal: <b>{svc['max']:,}</b>\n\n"
        f"💰 <b>Narx:</b> {p1000:,} so'm / 1 000 ta{disc_ln}\n\n"
        f"✏️ <b>Nechta buyurtma bermoqchisiz?</b>\n"
        "<i>Quyida raqam yozing:</i>"
    )


def _link_prompt_text(platform: str, section: str, link_override: dict | None = None) -> str:
    info = link_override or get_link_info(platform, section)
    return (
        f"🔗 <b>Link yuboring</b>\n\n"
        f"{info['prompt']}\n\n"
        f"📌 <b>Namuna:</b>\n"
        f"<code>{info['example']}</code>"
    )


def _comments_prompt_text(quantity: int) -> str:
    return (
        f"✏️ <b>Izohlarni yuboring</b>\n\n"
        "📌 Har bir izohni <b>yangi qatordan</b> yozing.\n"
        f"📊 Jami: <b>{quantity:,} ta</b> izoh kerak.\n\n"
        "<i>Misol:</i>\n"
        "<code>Ajoyib video!\n"
        "Juda foydali, rahmat!\n"
        "Zo'r kontent davom eting!</code>"
    )


def _order_summary_text(
    service_name: str, quantity: int, link: str,
    total_price: int, balance: int, discount: float,
    comments: str | None = None,
) -> str:
    enough     = balance >= total_price
    disc_ln    = f"\n🏷 Chegirma:  <b>{discount:+.0f}%</b>" if discount != 0 else ""
    comment_ln = f"\n✏️ Izohlar:   <b>{len(comments.splitlines())} ta</b>" if comments else ""
    status_ln  = (
        "✅ <b>Balansingiz yetarli</b>"
        if enough else
        f"❌ <b>Balans yetarli emas!</b>\n"
        f"   Kerak: {total_price:,}  |  Bor: {balance:,} so'm"
    )
    return (
        f"📦 <b>Buyurtma tafsilotlari</b>\n\n"
        f"{DIVIDER}\n"
        f"🏷 Xizmat:   <b>{service_name}</b>\n"
        f"🔢 Miqdor:   <b>{quantity:,}</b>\n"
        f"🔗 Link:     <code>{link}</code>{comment_ln}\n"
        f"💰 Narx:     <b>{total_price:,} so'm</b>{disc_ln}\n"
        f"💳 Balans:   <b>{balance:,} so'm</b>\n"
        f"{DIVIDER}\n\n"
        f"{status_ln}"
    )


# ── Callback handlerlari ──────────────────────────────────────

@router.callback_query(F.data == "coming_soon")
async def cb_coming_soon(call: CallbackQuery):
    await call.answer("🔜 Tez orada qo'shiladi! Kuting...", show_alert=True)


@router.callback_query(F.data == "services")
async def cb_services(call: CallbackQuery):
    await call.message.edit_text(
        f"🛍 <b>Xizmatlar</b>\n\n{DIVIDER}\nPlatformani tanlang 👇",
        reply_markup=platforms_keyboard(get_platform_names()),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("plat_"))
async def cb_platform(call: CallbackQuery):
    platform = call.data[5:]
    if is_coming_soon(platform):
        await call.answer("🔜 Tez orada qo'shiladi!", show_alert=True)
        return
    await call.message.edit_text(
        f"🛍 <b>{platform}</b>\n\n{DIVIDER}\nBo'limni tanlang 👇",
        reply_markup=sections_keyboard(platform, get_section_names(platform)),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("sec_"))
async def cb_section(call: CallbackQuery):
    parts    = call.data[4:].split("|||", 1)
    platform = parts[0]
    section  = parts[1] if len(parts) > 1 else ""
    services = get_section_services(platform, section)
    if not services:
        await call.answer("🔜 Tez orada xizmatlar qo'shiladi!", show_alert=True)
        return
    await call.message.edit_text(
        f"🛍 <b>{platform}  ›  {section}</b>\n\n"
        f"{DIVIDER}\n"
        "Xizmatni tanlang 👇\n"
        "<i>(Narxlar har 1 000 ta uchun)</i>",
        reply_markup=services_list_keyboard(
            platform, section, services, price_per_1000_uzs, get_markup
        ),
        parse_mode="HTML",
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

    discount = await get_user_discount(call.from_user.id)
    markup   = get_markup(svc)

    # Chegirma bo'lsa — markup ni moslashtir
    if discount != 0:
        cost     = cost_price_uzs_per_item(svc["rate"]) * 1000
        base     = price_per_1000_uzs(svc["rate"], markup)
        profit   = base - cost
        adjusted = profit * (1 - discount / 100)
        effective = max(cost, cost + adjusted)
        if cost > 0:
            markup = max(0.0, (effective / cost - 1) * 100)

    platform, section = find_platform_section(service_id)

    await state.update_data(
        service_id      = service_id,
        service_name    = svc["name"],
        platform        = platform,
        section         = section,
        min_q           = svc["min"],
        max_q           = svc["max"],
        rate            = svc["rate"],
        markup          = markup,
        link_override   = svc.get("link_override"),
        custom_comments = svc.get("custom_comments", False),
    )
    await state.set_state(OrderState.waiting_quantity)

    await call.message.edit_text(
        _service_detail_text(svc, markup, discount),
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer()


# ── FSM: Miqdor ───────────────────────────────────────────────

@router.message(OrderState.waiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    text = message.text.strip().replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("❌ Faqat <b>raqam</b> kiriting!", parse_mode="HTML")
        return

    qty = int(text)
    if qty < data["min_q"] or qty > data["max_q"]:
        await message.answer(
            f"❌ Miqdor <b>{data['min_q']:,}</b> — <b>{data['max_q']:,}</b> oralig'ida bo'lishi kerak!",
            parse_mode="HTML",
        )
        return

    markup      = data.get("markup")
    total_price = calc_price_uzs(data["rate"], qty, markup)
    await state.update_data(quantity=qty, total_price=total_price)
    await state.set_state(OrderState.waiting_link)

    await message.answer(
        _link_prompt_text(data["platform"], data["section"], data.get("link_override")),
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )


# ── FSM: Link ─────────────────────────────────────────────────

@router.message(OrderState.waiting_link)
async def process_link(message: Message, state: FSMContext):
    link = message.text.strip()
    data = await state.get_data()
    link_override = data.get("link_override")
    info = link_override or get_link_info(data.get("platform", ""), data.get("section", ""))

    if not validate_link(link, info.get("validate", "url")):
        await message.answer(
            f"❌ <b>Noto'g'ri link!</b>\n\n"
            f"📌 <b>To'g'ri format:</b>\n"
            f"<code>{info['example']}</code>\n\n"
            "Qaytadan yuboring:",
            parse_mode="HTML",
        )
        return

    await state.update_data(link=link)

    if data.get("custom_comments"):
        await state.set_state(OrderState.waiting_comments)
        await message.answer(
            _comments_prompt_text(data.get("quantity", 1)),
            parse_mode="HTML",
        )
        return

    await _show_order_summary(message, state)


# ── FSM: Custom Comments ──────────────────────────────────────

@router.message(OrderState.waiting_comments)
async def process_comments(message: Message, state: FSMContext):
    lines = [ln.strip() for ln in message.text.strip().splitlines() if ln.strip()]
    if not lines:
        await message.answer("❌ Kamida <b>1 ta</b> izoh yozing!", parse_mode="HTML")
        return

    data = await state.get_data()
    qty  = data.get("quantity", 1)
    if len(lines) < qty:
        await message.answer(
            f"⚠️ Siz <b>{len(lines)}</b> ta izoh yozdingiz, lekin <b>{qty}</b> ta kerak.\n"
            "Izohlar takrorlangan holda ishlatiladi.",
            parse_mode="HTML",
        )

    await state.update_data(comments="\n".join(lines))
    await _show_order_summary(message, state)


# ── Buyurtma xulosasi ─────────────────────────────────────────

async def _show_order_summary(message: Message, state: FSMContext):
    data        = await state.get_data()
    markup      = data.get("markup")
    total_price = calc_price_uzs(data["rate"], data["quantity"], markup)
    balance     = await get_balance(message.from_user.id)
    discount    = await get_user_discount(message.from_user.id)
    comments    = data.get("comments")

    await state.update_data(total_price=total_price)

    enough = balance >= total_price
    await message.answer(
        _order_summary_text(
            data["service_name"], data["quantity"],
            data["link"], total_price, balance, discount, comments,
        ),
        reply_markup=(
            order_confirm_keyboard(data["service_id"], data["quantity"])
            if enough else back_to_main()
        ),
        parse_mode="HTML",
    )
    if not enough:
        await state.clear()


# ── Tasdiqlash ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("confirm_order_"))
async def cb_confirm_order(call: CallbackQuery, state: FSMContext, bot: Bot):
    data         = await state.get_data()
    service_id   = data.get("service_id")
    service_name = data.get("service_name")
    platform     = data.get("platform", "")
    quantity     = data.get("quantity")
    link         = data.get("link")
    total_price  = data.get("total_price")
    comments     = data.get("comments")

    if not all([service_id, quantity, link, total_price]):
        await call.answer("❌ Ma'lumot topilmadi. Qaytadan urinib ko'ring.", show_alert=True)
        await state.clear()
        return

    if not await deduct_balance(call.from_user.id, total_price):
        await call.answer("❌ Balansingiz yetarli emas!", show_alert=True)
        await state.clear()
        return

    result       = await place_order(service_id, link, quantity, comments=comments)
    smm_order_id = result.get("order")

    if not smm_order_id:
        # Pul qaytarish
        await deduct_balance(call.from_user.id, -total_price)
        await call.message.edit_text(
            f"❌ <b>Buyurtma berishda xatolik!</b>\n\n"
            f"💰 Pulingiz qaytarildi: <b>{total_price:,} so'm</b>\n\n"
            "Qayta urinib ko'ring yoki admin bilan bog'laning.",
            reply_markup=order_error_keyboard(service_id, quantity, ADMIN_USERNAME),
            parse_mode="HTML",
        )
        await call.answer()
        await state.clear()
        return

    await create_order(
        call.from_user.id, smm_order_id, service_id,
        service_name, platform, link, quantity, total_price,
    )

    # Referal foiz hisoblash
    from database import get_referrer, add_referral_earning
    from config import REFERRAL_PERCENT
    referrer_id = await get_referrer(call.from_user.id)
    if referrer_id:
        percent_amt = round(total_price * REFERRAL_PERCENT / 100)
        await add_referral_earning(
            referrer_id, call.from_user.id, percent_amt, total_price, "percent"
        )
        user = call.from_user
        name = f"@{user.username}" if user.username else user.full_name
        try:
            await bot.send_message(
                referrer_id,
                f"💰 <b>Referal daromad!</b>\n\n"
                f"👤 <b>{name}</b> buyurtma berdi\n"
                f"➕ <b>+{percent_amt:,} so'm</b> ({REFERRAL_PERCENT:.0f}%) tushdi!",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await state.clear()
    await call.message.edit_text(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"{DIVIDER}\n"
        f"🔖 ID:        <code>#{smm_order_id}</code>\n"
        f"🏷 Xizmat:    <b>{service_name}</b>\n"
        f"🔢 Miqdor:    <b>{quantity:,}</b>\n"
        f"💰 To'langan: <b>{total_price:,} so'm</b>\n"
        f"{DIVIDER}\n\n"
        "⏳ Holat: <b>Kutilmoqda</b>\n"
        "📋 <b>Buyurtmalarim</b> bo'limida kuzatib boring.\n"
        "<i>Bajarish vaqti xizmat turiga qarab 1 daqiqadan bir necha soatgacha.</i>",
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer("✅ Buyurtma qabul qilindi!")


# ── Qayta urinish ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("retry_order_"))
async def cb_retry_order(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    try:
        service_id = int(parts[2])
        quantity   = int(parts[3])
    except (IndexError, ValueError):
        await call.answer("❌ Xatolik!", show_alert=True)
        return

    svc = find_service(service_id)
    if not svc:
        await call.answer("❌ Xizmat topilmadi!", show_alert=True)
        return

    markup          = get_markup(svc)
    total_price     = calc_price_uzs(svc["rate"], quantity, markup)
    platform, section = find_platform_section(service_id)

    await state.update_data(
        service_id      = service_id,
        service_name    = svc["name"],
        platform        = platform,
        section         = section,
        min_q           = svc["min"],
        max_q           = svc["max"],
        rate            = svc["rate"],
        markup          = markup,
        quantity        = quantity,
        total_price     = total_price,
        link_override   = svc.get("link_override"),
        custom_comments = svc.get("custom_comments", False),
    )
    await state.set_state(OrderState.waiting_link)

    await call.message.edit_text(
        f"🔄 <b>Qayta buyurtma</b>\n\n"
        f"{DIVIDER}\n"
        f"🏷 Xizmat:   <b>{svc['name']}</b>\n"
        f"🔢 Miqdor:   <b>{quantity:,}</b>\n"
        f"💰 Narx:     <b>{total_price:,} so'm</b>\n"
        f"{DIVIDER}\n\n"
        + _link_prompt_text(platform, section, svc.get("link_override")),
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer()
