"""
services.py — Zendor SMM Bot
Xizmatlar, platformalar, bo'limlar, buyurtma berish.
2026 yangi dizayn.
"""

import os
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from smm_api import (
    get_platform_names, get_section_names, get_section_services,
    find_service, calc_price_uzs, price_per_1000_uzs,
    get_markup, cost_price_uzs_per_item, place_order, PLATFORMS,
)
from database import get_balance, deduct_balance, create_order, get_user_discount
from handlers.link_examples import get_link_info, validate_link
from keyboards.menus import (
    platforms_keyboard, sections_keyboard, services_list_keyboard,
    order_confirm_keyboard, order_error_keyboard, back_to_main,
)

router = Router()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")
COMING_SOON    = {"🎮 O'yinlar", "⭐️ Stars"}


class OrderState(StatesGroup):
    waiting_quantity = State()
    waiting_link     = State()
    waiting_comments = State()  # ✅ Custom Comments uchun


# ── Yordamchi funksiyalar ─────────────────────────────────────

def _find_platform_section(service_id: int) -> tuple[str, str]:
    for platform, sections in PLATFORMS.items():
        if not isinstance(sections, dict):
            continue
        for section, services in sections.items():
            if not isinstance(services, list):
                continue
            for s in services:
                if isinstance(s, dict) and s.get("service") == service_id:
                    return platform, section
    return "", ""


def _svc_detail_text(svc: dict, markup: float, discount: float = 0) -> str:
    p1000   = price_per_1000_uzs(svc["rate"], markup)
    refill  = "\n♻️ <b>Refill kafolatli</b>" if svc.get("refill") else ""
    discount_line = f"\n🏷 Sizning chegirmangiz: <b>{discount:+.0f}%</b>" if discount != 0 else ""

    return (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>{svc['name']}</b>{refill}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 {svc.get('description', '—')}\n\n"
        f"📊 <b>Miqdor chegarasi:</b>\n"
        f"├ Minimal: <b>{svc['min']:,}</b>\n"
        f"└ Maksimal: <b>{svc['max']:,}</b>\n\n"
        f"💰 <b>Narx:</b> {p1000:,} so'm / 1 000 ta{discount_line}\n\n"
        f"✏️ <b>Nechta buyurtma bermoqchisiz?</b>\n"
        f"<i>Quyida raqam yozing:</i>"
    )


def _get_link_info_for_service(platform: str, section: str, link_override: dict | None) -> dict:
    """link_override bo'lsa uni, aks holda standartni qaytaradi."""
    if link_override:
        return link_override
    return get_link_info(platform, section)


def _link_prompt_text(platform: str, section: str, link_override: dict | None = None) -> str:
    info = _get_link_info_for_service(platform, section, link_override)
    return (
        f"🔗 <b>Link yuboring</b>\n\n"
        f"{info['prompt']}\n\n"
        f"📌 <b>Namuna:</b>\n"
        f"<code>{info['example']}</code>"
    )


def _comments_prompt_text(quantity: int) -> str:
    """Custom Comments so'rash matni."""
    return (
        f"✏️ <b>Izohlarni yuboring</b>\n\n"
        f"📌 Har bir izohni <b>yangi qatordan</b> yozing.\n"
        f"📊 Jami: <b>{quantity:,} ta</b> izoh kerak.\n\n"
        f"<i>Misol:</i>\n"
        f"<code>Ajoyib video!\n"
        f"Juda foydali, rahmat!\n"
        f"Zo'r kontent davom eting!</code>"
    )


def _order_summary_text(
    service_name: str, quantity: int, link: str,
    total_price: int, balance: int, discount: float,
    comments: str | None = None,
) -> str:
    enough        = balance >= total_price
    discount_line = f"\n🏷 Chegirma: <b>{discount:+.0f}%</b>" if discount != 0 else ""
    comments_line = (
        f"\n✏️ Izohlar: <b>{len(comments.splitlines())} ta</b>"
        if comments else ""
    )
    status_line   = (
        "✅ <b>Balansingiz yetarli</b>" if enough else
        f"❌ <b>Balans yetarli emas!</b>\n"
        f"   Kerak: {total_price:,}  |  Bor: {balance:,} so'm"
    )

    return (
        f"📦 <b>Buyurtma tafsilotlari</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 Xizmat:  <b>{service_name}</b>\n"
        f"🔢 Miqdor:  <b>{quantity:,}</b>\n"
        f"🔗 Link:    <code>{link}</code>{comments_line}\n"
        f"💰 Narx:    <b>{total_price:,} so'm</b>{discount_line}\n"
        f"💳 Balans:  <b>{balance:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{status_line}"
    )


# ── Callback handlerlari ──────────────────────────────────────

@router.callback_query(F.data == "coming_soon")
async def cb_coming_soon(call: CallbackQuery):
    await call.answer("🔜 Tez orada qo'shiladi! Kuting...", show_alert=True)


@router.callback_query(F.data == "services")
async def cb_services(call: CallbackQuery):
    await call.message.edit_text(
        "🛍 <b>Xizmatlar</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Platformani tanlang 👇",
        reply_markup=platforms_keyboard(get_platform_names()),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("plat_"))
async def cb_platform(call: CallbackQuery):
    platform = call.data[5:]
    if platform in COMING_SOON:
        await call.answer("🔜 Tez orada qo'shiladi!", show_alert=True)
        return

    await call.message.edit_text(
        f"🛍 <b>{platform}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Bo'limni tanlang 👇",
        reply_markup=sections_keyboard(platform, get_section_names(platform)),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("sec_"))
async def cb_section(call: CallbackQuery):
    parts    = call.data[4:].split("|||", 1)
    platform = parts[0]
    section  = parts[1]

    services = get_section_services(platform, section)
    if not services:
        await call.answer("🔜 Tez orada xizmatlar qo'shiladi!", show_alert=True)
        return

    await call.message.edit_text(
        f"🛍 <b>{platform}  ›  {section}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Xizmatni tanlang 👇\n"
        f"(Narxlar har 1000 ta uchun amal qiladi)",
        reply_markup=services_list_keyboard(
            platform, section, services,
            price_per_1000_uzs, get_markup,
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

    if discount != 0:
        cost      = cost_price_uzs_per_item(svc["rate"]) * 1000
        base      = price_per_1000_uzs(svc["rate"], markup)
        profit    = base - cost
        adjusted  = profit * (1 - discount / 100)
        effective = max(cost, cost + adjusted)
        if cost > 0:
            markup = max(0, (effective / cost - 1) * 100)

    platform, section = _find_platform_section(service_id)

    await state.update_data(
        service_id      = service_id,
        service_name    = svc["name"],
        platform        = platform,
        section         = section,
        min_q           = svc["min"],
        max_q           = svc["max"],
        rate            = svc["rate"],
        markup          = markup,
        link_override   = svc.get("link_override"),   # ✅
        custom_comments = svc.get("custom_comments", False),  # ✅
    )
    await state.set_state(OrderState.waiting_quantity)

    await call.message.edit_text(
        _svc_detail_text(svc, markup, discount),
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer()


# ── FSM: miqdor → link → [izohlar] → tasdiqlash ──────────────

@router.message(OrderState.waiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("❌ Faqat <b>raqam</b> kiriting!", parse_mode="HTML")
        return

    quantity = int(text)
    data     = await state.get_data()
    min_q, max_q = data.get("min_q", 1), data.get("max_q", 99999)

    if not (min_q <= quantity <= max_q):
        await message.answer(
            f"❌ Miqdor <b>{min_q:,}</b> — <b>{max_q:,}</b> oralig'ida bo'lishi kerak!",
            parse_mode="HTML",
        )
        return

    await state.update_data(quantity=quantity)
    await state.set_state(OrderState.waiting_link)
    await message.answer(
        _link_prompt_text(
            data.get("platform", ""),
            data.get("section", ""),
            data.get("link_override"),
        ),
        parse_mode="HTML",
    )


@router.message(OrderState.waiting_link)
async def process_link(message: Message, state: FSMContext):
    link      = message.text.strip()
    data      = await state.get_data()
    platform  = data.get("platform", "")
    section   = data.get("section", "")
    link_info = _get_link_info_for_service(platform, section, data.get("link_override"))

    if not validate_link(link, link_info.get("validate", "url")):
        await message.answer(
            f"❌ <b>Noto'g'ri link!</b>\n\n"
            f"📌 <b>To'g'ri format:</b>\n"
            f"<code>{link_info['example']}</code>\n\n"
            f"Qaytadan yuboring:",
            parse_mode="HTML",
        )
        return

    await state.update_data(link=link)

    # ✅ Agar Custom Comments bo'lsa — izoh matnini so'raymiz
    if data.get("custom_comments"):
        await state.set_state(OrderState.waiting_comments)
        await message.answer(
            _comments_prompt_text(data.get("quantity", 1)),
            parse_mode="HTML",
        )
        return

    # Oddiy xizmat — to'g'ridan-to'g'ri tasdiqqa o'tamiz
    await _show_order_summary(message, state)


@router.message(OrderState.waiting_comments)
async def process_comments(message: Message, state: FSMContext):
    """Custom Comments matni qabul qilish."""
    comments = message.text.strip()
    if not comments:
        await message.answer("❌ Izoh matni bo'sh bo'lishi mumkin emas!", parse_mode="HTML")
        return

    lines    = [l.strip() for l in comments.splitlines() if l.strip()]
    data     = await state.get_data()
    quantity = data.get("quantity", 1)

    if len(lines) < 1:
        await message.answer(
            "❌ Kamida <b>1 ta</b> izoh yozing!\n"
            "Har bir izohni yangi qatordan yozing.",
            parse_mode="HTML",
        )
        return

    # Izohlar miqdori yetarli bo'lmasa ogohlantirish (lekin davom etadi)
    if len(lines) < quantity:
        await message.answer(
            f"⚠️ Siz <b>{len(lines)}</b> ta izoh yozdingiz, "
            f"lekin <b>{quantity}</b> ta kerak.\n"
            f"Izohlar takrorlangan holda ishlatiladi.",
            parse_mode="HTML",
        )

    # Izohlarni yangi qator bilan birlashtirish
    await state.update_data(comments="\n".join(lines))
    await _show_order_summary(message, state)


async def _show_order_summary(message: Message, state: FSMContext):
    """Buyurtma xulosasini ko'rsatish (link va comments tayyor bo'lgach)."""
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
            data["link"], total_price, balance, discount,
            comments,
        ),
        reply_markup=(
            order_confirm_keyboard(data["service_id"], data["quantity"])
            if enough else back_to_main()
        ),
        parse_mode="HTML",
    )
    if not enough:
        await state.clear()


@router.callback_query(F.data.startswith("confirm_order_"))
async def cb_confirm_order(call: CallbackQuery, state: FSMContext, bot: Bot):
    data         = await state.get_data()
    service_id   = data.get("service_id")
    service_name = data.get("service_name")
    platform     = data.get("platform", "")
    quantity     = data.get("quantity")
    link         = data.get("link")
    total_price  = data.get("total_price")
    comments     = data.get("comments")  # ✅ Custom Comments

    if not all([service_id, quantity, link, total_price]):
        await call.answer("❌ Ma'lumot topilmadi. Qaytadan urinib ko'ring.", show_alert=True)
        await state.clear()
        return

    if not await deduct_balance(call.from_user.id, total_price):
        await call.answer("❌ Balansingiz yetarli emas!", show_alert=True)
        await state.clear()
        return

    # ✅ comments ni place_order ga uzatamiz
    result       = await place_order(service_id, link, quantity, comments=comments)
    smm_order_id = result.get("order")

    if not smm_order_id:
        await deduct_balance(call.from_user.id, -total_price)
        await call.message.edit_text(
            f"❌ <b>Buyurtma berishda xatolik!</b>\n\n"
            f"💰 Pulingiz qaytarildi: <b>{total_price:,} so'm</b>\n\n"
            f"Qayta urinib ko'ring yoki admin bilan bog'laning.",
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

    # Referal foiz
    from database import get_referrer, add_referral_earning
    from config import REFERRAL_PERCENT
    referrer_id = await get_referrer(call.from_user.id)
    if referrer_id:
        percent_amount = round(total_price * REFERRAL_PERCENT / 100)
        await add_referral_earning(referrer_id, call.from_user.id, percent_amount, total_price, "percent")
        user = call.from_user
        name = f"@{user.username}" if user.username else user.full_name
        try:
            await bot.send_message(
                referrer_id,
                f"💰 <b>Referal daromad!</b>\n\n"
                f"👤 <b>{name}</b> buyurtma berdi\n"
                f"➕ <b>+{percent_amount:,} so'm</b> ({REFERRAL_PERCENT:.0f}%) tushdi!",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await state.clear()
    await call.message.edit_text(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔖 ID:      <code>#{smm_order_id}</code>\n"
        f"🏷 Xizmat:  <b>{service_name}</b>\n"
        f"🔢 Miqdor:  <b>{quantity:,}</b>\n"
        f"💰 To'langan: <b>{total_price:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ Holat: <b>Kutilmoqda</b>\n"
        f"📋 'Buyurtmalarim' dan kuzatib boring.",
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer("✅ Buyurtma qabul qilindi!")


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
    platform, section = _find_platform_section(service_id)
    link_override   = svc.get("link_override")
    custom_comments = svc.get("custom_comments", False)

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
        link_override   = link_override,
        custom_comments = custom_comments,
    )
    await state.set_state(OrderState.waiting_link)

    await call.message.edit_text(
        f"🔄 <b>Qayta buyurtma</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 Xizmat:  <b>{svc['name']}</b>\n"
        f"🔢 Miqdor:  <b>{quantity:,}</b>\n"
        f"💰 Narx:    <b>{total_price:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        + _link_prompt_text(platform, section, link_override),
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )
    await call.answer()