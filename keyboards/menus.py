from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def main_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📦 Xizmatlar"),
        KeyboardButton(text="💰 Balans")
    )
    builder.row(
        KeyboardButton(text="🗂 Buyurtmalarim"),
        KeyboardButton(text="ℹ️ Yordam")
    )
    builder.row(KeyboardButton(text="🎁 Referal"))
    return builder.as_markup(resize_keyboard=True)

def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 Xizmatlar", callback_data="services"),
        InlineKeyboardButton(text="💰 Balans", callback_data="balance")
    )
    builder.row(
        InlineKeyboardButton(text="🗂 Buyurtmalarim", callback_data="my_orders"),
        InlineKeyboardButton(text="ℹ️ Yordam", callback_data="support")
    )
    builder.row(InlineKeyboardButton(text="🎁 Referal dasturi", callback_data="referral"))
    return builder.as_markup()

def balance_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Balansni to'ldirish", callback_data="deposit"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    return builder.as_markup()

def services_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✈️ Telegram", callback_data="platform_telegram"))
    builder.row(InlineKeyboardButton(text="📸 Instagram", callback_data="platform_instagram"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"))
    return builder.as_markup()

def service_list_keyboard(services: list, platform: str, page: int = 0, page_size: int = 8) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * page_size
    end = start + page_size
    page_services = services[start:end]

    for s in page_services:
        name = s.get("name", "")[:35]
        sid = s.get("service")
        builder.row(InlineKeyboardButton(
            text=f"{'✈️' if platform == 'telegram' else '📸'} {name}",
            callback_data=f"svc_{sid}"
        ))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"svc_page_{platform}_{page - 1}"))
    if end < len(services):
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"svc_page_{platform}_{page + 1}"))
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="services"))
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

def admin_deposit_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"adm_confirm_{deposit_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm_reject_{deposit_id}")
    )
    return builder.as_markup()