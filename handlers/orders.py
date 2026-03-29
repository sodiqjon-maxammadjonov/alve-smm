from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_user_orders
from smm_api import get_order_status
from keyboards.menus import back_to_main

router = Router()

STATUS_EMOJI = {
    "Pending": "⏳",
    "In progress": "🔄",
    "Processing": "🔄",
    "Completed": "✅",
    "Partial": "⚠️",
    "Canceled": "❌",
    "Refunded": "💸",
}

@router.callback_query(F.data == "my_orders")
async def cb_my_orders(call: CallbackQuery):
    orders = await get_user_orders(call.from_user.id)
    if not orders:
        await call.message.edit_text(
            "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
            reply_markup=back_to_main(),
            parse_mode="HTML"
        )
        await call.answer()
        return

    lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
    for o in orders:
        smm_id = o.get("smm_order_id")
        status = o.get("status", "Pending")
        emoji = STATUS_EMOJI.get(status, "❓")
        name = o.get("service_name", "")[:30]
        qty = o.get("quantity", 0)
        price = o.get("price_uzs", 0)
        lines.append(
            f"{emoji} <b>#{smm_id}</b> | {name}\n"
            f"   🔢 {qty:,} | 💰 {price:,.0f} so'm | {status}\n"
        )

    await call.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )
    await call.answer()