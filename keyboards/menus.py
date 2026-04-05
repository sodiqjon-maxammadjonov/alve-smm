"""
keyboards/menus.py — Zendor SMM Bot
Barcha klaviaturalar bir joyda.

YANGI TUGMA QO'SHISH:
  Tegishli funksiyaga InlineKeyboardButton qo'shing.
  Yangi klaviatura kerak bo'lsa — yangi funksiya oching.
"""

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# ═══════════════════════════════════════════════════════════════
#  REPLY KEYBOARD — Pastki doimiy menyu
# ═══════════════════════════════════════════════════════════════

def main_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🛍 Xizmatlar"),
        KeyboardButton(text="💰 Balans"),
    )
    builder.row(
        KeyboardButton(text="📋 Buyurtmalarim"),
        KeyboardButton(text="🎁 Referal"),
    )
    builder.row(KeyboardButton(text="🆘 Yordam"))
    return builder.as_markup(resize_keyboard=True, is_persistent=True)


# ═══════════════════════════════════════════════════════════════
#  BOSH MENYU — Inline
# ═══════════════════════════════════════════════════════════════

def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🛍  Xizmatlar",      callback_data="services"),
        InlineKeyboardButton(text="💰  Balans",          callback_data="balance"),
    )
    builder.row(
        InlineKeyboardButton(text="📋  Buyurtmalarim",  callback_data="my_orders"),
        InlineKeyboardButton(text="🆘  Yordam",          callback_data="support"),
    )
    builder.row(
        InlineKeyboardButton(text="🎁  Referal dasturi", callback_data="referral"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  BALANS MENYU
# ═══════════════════════════════════════════════════════════════

def balance_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕  Balans to'ldirish", callback_data="deposit"),
    )
    builder.row(
        InlineKeyboardButton(text="📋  Buyurtmalarim",    callback_data="my_orders"),
        InlineKeyboardButton(text="🏠  Bosh menyu",       callback_data="main_menu"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  DEPOZIT KLAVIATURALAR
# ═══════════════════════════════════════════════════════════════

def cancel_deposit_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌  Bekor qilish", callback_data="cancel_deposit"),
    )
    return builder.as_markup()


def admin_contact_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="👨‍💼  Admin bilan bog'lanish",
            url=f"https://t.me/{admin_username.lstrip('@')}",
        )
    )
    builder.row(
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  ADMIN — Depozit tasdiqlash / rad etish
# ═══════════════════════════════════════════════════════════════

def admin_deposit_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅  Tasdiqlash",
            callback_data=f"adm_confirm_{deposit_id}",
        ),
        InlineKeyboardButton(
            text="❌  Rad etish",
            callback_data=f"adm_reject_{deposit_id}",
        ),
    )
    return builder.as_markup()


def confirm_action_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅  Ha, tasdiqlayman",
            callback_data=f"adm_confirm_yes_{deposit_id}",
        ),
        InlineKeyboardButton(
            text="↩️  Bekor",
            callback_data=f"adm_back_{deposit_id}",
        ),
    )
    return builder.as_markup()


def reject_ask_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️  Sabab yozaman",
            callback_data=f"adm_reject_write_{deposit_id}",
        ),
        InlineKeyboardButton(
            text="⚡  Shunchaki rad",
            callback_data=f"adm_reject_yes_{deposit_id}_",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="↩️  Orqaga", callback_data=f"adm_back_{deposit_id}"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  XIZMATLAR — Platform, Bo'lim, Xizmat
# ═══════════════════════════════════════════════════════════════

# Coming soon platformalar — tugma ko'rinadi lekin "Tez orada" deydi
COMING_SOON_PLATFORMS: set[str] = {"🎮 O'yinlar"}


def platforms_keyboard(platform_names: list[str]) -> InlineKeyboardMarkup:
    """2 ustunli platform tanlash klaviaturasi."""
    builder   = InlineKeyboardBuilder()
    active    = [n for n in platform_names if n not in COMING_SOON_PLATFORMS]
    soon      = [n for n in platform_names if n in COMING_SOON_PLATFORMS]

    for i in range(0, len(active), 2):
        chunk = active[i:i + 2]
        builder.row(*[
            InlineKeyboardButton(text=n, callback_data=f"plat_{n}")
            for n in chunk
        ])
    for n in soon:
        builder.row(
            InlineKeyboardButton(text=f"{n}  🔜", callback_data="coming_soon"),
        )
    builder.row(
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


def sections_keyboard(platform: str, section_names: list[str]) -> InlineKeyboardMarkup:
    """2 ustunli bo'lim tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for i in range(0, len(section_names), 2):
        chunk = section_names[i:i + 2]
        builder.row(*[
            InlineKeyboardButton(
                text=s,
                callback_data=f"sec_{platform}|||{s}",
            )
            for s in chunk
        ])
    builder.row(
        InlineKeyboardButton(text="↩️  Platformalar", callback_data="services"),
        InlineKeyboardButton(text="🏠  Bosh menyu",   callback_data="main_menu"),
    )
    return builder.as_markup()


def services_list_keyboard(
    platform: str,
    section: str,
    services: list,
    price_per_1000_fn,
    get_markup_fn,
) -> InlineKeyboardMarkup:
    """Xizmatlar ro'yxati — har xizmat alohida qatorda."""
    builder = InlineKeyboardBuilder()
    for s in services:
        markup = get_markup_fn(s)
        p1000  = price_per_1000_fn(s["rate"], markup)
        refill = " ♻️" if s.get("refill") else ""
        name   = s["name"][:32]
        builder.row(
            InlineKeyboardButton(
                text=f"{name}{refill}  —  {p1000:,} so'm",
                callback_data=f"svc_{s['service']}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=f"↩️  {section[:20]}",
            callback_data=f"plat_{platform}",
        ),
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


def order_confirm_keyboard(service_id: int, quantity: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅  Tasdiqlash",
            callback_data=f"confirm_order_{service_id}_{quantity}",
        ),
        InlineKeyboardButton(text="❌  Bekor", callback_data="services"),
    )
    return builder.as_markup()


def order_error_keyboard(
    service_id: int, quantity: int, admin_username: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔄  Qayta urinish",
            callback_data=f"retry_order_{service_id}_{quantity}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="👨‍💼  Admin",
            url=f"https://t.me/{admin_username.lstrip('@')}",
        ),
        InlineKeyboardButton(text="🏠  Menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  NAVIGATSIYA
# ═══════════════════════════════════════════════════════════════

def back_to_main() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


def back_and_home(back_data: str, back_label: str = "↩️  Orqaga") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=back_label,       callback_data=back_data),
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  REFERAL
# ═══════════════════════════════════════════════════════════════

def referral_keyboard(user_id: int, bot_username: str) -> InlineKeyboardMarkup:
    ref_link   = f"https://t.me/{bot_username}?start=REF_{user_id}"
    share_text = (
        f"🚀 Telegram, Instagram, TikTok, YouTube uchun eng arzon SMM!\n\n"
        f"✅ Ishonchli  |  ⚡ Tez  |  💰 Arzon\n\n"
        f"👇 Ro'yxatdan o'ting:\n{ref_link}"
    )
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📤  Havolani ulashish",
            switch_inline_query=share_text,
        )
    )
    builder.row(
        InlineKeyboardButton(text="📋  Referal tarixi", callback_data="referral_history_0"),
        InlineKeyboardButton(text="🏠  Bosh menyu",     callback_data="main_menu"),
    )
    return builder.as_markup()


def referral_history_keyboard(
    page: int, has_prev: bool, has_next: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav = []
    if has_prev:
        nav.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"referral_history_{page - 1}")
        )
    if has_next:
        nav.append(
            InlineKeyboardButton(text="➡️", callback_data=f"referral_history_{page + 1}")
        )
    if nav:
        builder.row(*nav)
    builder.row(
        InlineKeyboardButton(text="↩️  Referal",   callback_data="referral"),
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  YORDAM (SUPPORT)
# ═══════════════════════════════════════════════════════════════

def support_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="💬  Admin bilan bog'lanish",
            url=f"https://t.me/{admin_username.lstrip('@')}",
        )
    )
    builder.row(
        InlineKeyboardButton(text="🏠  Bosh menyu", callback_data="main_menu"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════════

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊  Statistika",       callback_data="adm_stats"),
        InlineKeyboardButton(text="👥  Foydalanuvchilar", callback_data="adm_users"),
    )
    builder.row(
        InlineKeyboardButton(text="📦  Buyurtmalar", callback_data="adm_orders_0_all"),
        InlineKeyboardButton(text="💰  Depozitlar",  callback_data="adm_deposits"),
    )
    builder.row(
        InlineKeyboardButton(text="⏳  Kutayotgan cheklar", callback_data="adm_pending"),
        InlineKeyboardButton(text="🏆  Top 10",             callback_data="adm_top"),
    )
    builder.row(
        InlineKeyboardButton(text="📢  Broadcast", callback_data="adm_broadcast"),
    )
    return builder.as_markup()


def orders_filter_keyboard(current: str, page: int) -> InlineKeyboardBuilder:
    """Buyurtmalar filtr tugmalari — builder qaytaradi (navigatsiya keyinchalik qo'shiladi)."""
    builder = InlineKeyboardBuilder()
    filters = [
        ("📋 Hammasi",    "all"),
        ("⏳ Kutish",     "Pending"),
        ("🔄 Jarayon",   "In progress"),
        ("✅ Bajarildi",  "Completed"),
        ("❌ Bekor",      "Canceled"),
    ]
    r1, r2 = [], []
    for i, (label, key) in enumerate(filters):
        prefix = "▸ " if key == current else ""
        btn = InlineKeyboardButton(
            text=f"{prefix}{label}",
            callback_data=f"adm_orders_0_{key}",
        )
        (r1 if i < 3 else r2).append(btn)
    builder.row(*r1)
    builder.row(*r2)
    return builder
