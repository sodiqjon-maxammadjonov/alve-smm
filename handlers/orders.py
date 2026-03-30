from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_user_orders, update_order_status
from smm_api import get_order_status
from keyboards.menus import back_to_main
import asyncio

router = Router()

STATUS_UZ = {
    "Pending":     "⏳ Kutilmoqda",
    "In progress": "🔄 Bajarilmoqda",
    "Processing":  "🔄 Jarayonda",
    "Completed":   "✅ Bajarildi",
    "Partial":     "⚠️ Qisman bajarildi",
    "Canceled":    "❌ Bekor qilindi",
    "Refunded":    "💸 Qaytarildi",
}

@router.callback_query(F.data == "my_orders")
async def cb_my_orders(call: CallbackQuery):
    await call.answer()
    orders = await get_user_orders(call.from_user.id)

    if not orders:
        await call.message.edit_text(
            "📦 <b>Buyurtmalarim</b>\n\nSizda hali buyurtma yo'q.",
            reply_markup=back_to_main(),
            parse_mode="HTML"
        )
        return

    # Peakerr dan real statuslarni olish
    async def fetch_status(order):
        smm_id = order.get("smm_order_id")
        if smm_id:
            try:
                data = await get_order_status(smm_id)
                # Peakerr javobidan status olish
                status = data.get("status", order.get("status", "Pending"))
                # DB ni ham yangilab qo'yamiz
                await update_order_status(smm_id, status)
                return status
            except:
                pass
        return order.get("status", "Pending")

    # Barcha orderlar uchun parallel status olish
    statuses = await asyncio.gather(*[fetch_status(o) for o in orders])

    lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
    for o, status in zip(orders, statuses):
        smm_id = o.get("smm_order_id")
        status_text = STATUS_UZ.get(status, f"❓ {status}")
        name = o.get("service_name", "")[:30]
        qty = o.get("quantity", 0)
        price = o.get("price_uzs", 0)
        lines.append(
            f"<b>#{smm_id}</b> | {name}\n"
            f"   🔢 {qty:,} | 💰 {price:,.0f} so'm\n"
            f"   {status_text}\n"
        )

    await call.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )