import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from database import get_user_orders, update_order_status, get_pool
from smm_api import get_order_status
from keyboards.menus import back_to_main

router = Router()
logger = logging.getLogger(__name__)

STATUS_UZ = {
    "Pending":     "⏳ Kutilmoqda",
    "In Progress": "🔄 Bajarilmoqda",
    "In progress": "🔄 Bajarilmoqda",
    "Processing":  "🔄 Jarayonda",
    "Completed":   "✅ Bajarildi",
    "Partial":     "⚠️ Qisman bajarildi",
    "Canceled":    "❌ Bekor qilindi",
    "Cancelled":   "❌ Bekor qilindi",
    "Refunded":    "💸 Qaytarildi",
}


async def fetch_and_update_status(order: dict) -> str:
    """
    Peakerr API dan real statusni oladi va DB ni yangilaydi.
    API javobi: {"charge":"0.27","start_count":"3572","status":"Completed","remains":"0","currency":"USD"}
    """
    smm_id = order.get("smm_order_id")
    db_status = order.get("status", "Pending")

    # Tugagan buyurtmalarni qayta tekshirmaymiz
    if db_status in ("Completed", "Canceled", "Cancelled", "Refunded", "Partial"):
        return db_status

    if not smm_id:
        return db_status

    try:
        data = await get_order_status(smm_id)

        # API xato qaytarsa
        if not data or "error" in data:
            logger.warning(f"Order {smm_id} API error: {data}")
            return db_status

        # "status" field ni olamiz
        new_status = data.get("status", db_status)

        # DB ni yangilaymiz agar o'zgarmagan bo'lsa
        if new_status != db_status:
            await update_order_status(smm_id, new_status)
            logger.info(f"Order {smm_id}: {db_status} -> {new_status}")

        return new_status

    except Exception as e:
        logger.warning(f"fetch_and_update_status error for {smm_id}: {e}")
        return db_status


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

    # Barcha aktiv orderlar uchun parallel holda API dan status olamiz
    statuses = await asyncio.gather(
        *[fetch_and_update_status(o) for o in orders]
    )

    lines = ["📦 <b>Buyurtmalarim</b> (oxirgi 20 ta):\n"]
    for o, status in zip(orders, statuses):
        smm_id = o.get("smm_order_id")
        status_text = STATUS_UZ.get(status, f"❓ {status}")
        name = (o.get("service_name") or "")[:30]
        qty = o.get("quantity", 0)
        price = o.get("price_uzs", 0)
        lines.append(
            f"<b>#{smm_id}</b> — {name}\n"
            f"   🔢 {qty:,} | 💰 {price:,.0f} so'm\n"
            f"   {status_text}\n"
        )

    await call.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_main(),
        parse_mode="HTML"
    )


# ── Background auto-updater ───────────────────────────────────

async def auto_update_orders(bot: Bot):
    """
    Har 5 daqiqada barcha aktiv buyurtmalar statusini yangilaydi.
    Tugallangan buyurtma egasiga xabar yuboradi.
    """
    logger.info("Auto-updater ishga tushdi")
    from keyboards.menus import back_to_main as btm

    while True:
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                # Faqat tugamagan buyurtmalar
                rows = await conn.fetch(
                    """SELECT o.id, o.smm_order_id, o.user_id, o.service_name,
                              o.quantity, o.price_uzs, o.status
                       FROM orders o
                       WHERE o.status NOT IN ('Completed','Canceled','Cancelled','Refunded','Partial')
                       ORDER BY o.created_at DESC
                       LIMIT 100"""
                )

            orders = [dict(r) for r in rows]
            if not orders:
                await asyncio.sleep(300)
                continue

            logger.info(f"Auto-update: {len(orders)} ta aktiv buyurtma tekshirilmoqda")

            for order in orders:
                smm_id = order.get("smm_order_id")
                old_status = order.get("status", "Pending")
                if not smm_id:
                    continue

                try:
                    data = await get_order_status(smm_id)
                    if not data or "error" in data:
                        continue

                    new_status = data.get("status", old_status)

                    if new_status != old_status:
                        await update_order_status(smm_id, new_status)
                        logger.info(f"Auto-update #{smm_id}: {old_status} -> {new_status}")

                        # Foydalanuvchiga xabar yuboramiz faqat muhim o'zgarishlarda
                        if new_status in ("Completed", "Partial", "Canceled", "Cancelled"):
                            status_text = STATUS_UZ.get(new_status, new_status)
                            svc_name = (order.get("service_name") or "")[:30]
                            qty = order.get("quantity", 0)

                            if new_status == "Completed":
                                msg = (
                                    f"✅ <b>Buyurtma bajarildi!</b>\n\n"
                                    f"🏷 {svc_name}\n"
                                    f"🔢 Miqdor: {qty:,}\n"
                                    f"🔖 ID: #{smm_id}"
                                )
                            elif new_status == "Partial":
                                remains = data.get("remains", "?")
                                msg = (
                                    f"⚠️ <b>Buyurtma qisman bajarildi</b>\n\n"
                                    f"🏷 {svc_name}\n"
                                    f"🔢 Qolgan: {remains}\n"
                                    f"🔖 ID: #{smm_id}"
                                )
                            else:
                                msg = (
                                    f"❌ <b>Buyurtma bekor qilindi</b>\n\n"
                                    f"🏷 {svc_name}\n"
                                    f"🔖 ID: #{smm_id}\n\n"
                                    f"Muammo bo'lsa admin bilan bog'laning."
                                )

                            try:
                                await bot.send_message(
                                    chat_id=order["user_id"],
                                    text=msg,
                                    reply_markup=btm(),
                                    parse_mode="HTML"
                                )
                            except Exception:
                                pass

                    # API ni zo'riqtirmaslik uchun kichik pauza
                    await asyncio.sleep(0.3)

                except Exception as e:
                    logger.warning(f"Order {smm_id} update error: {e}")
                    continue

        except Exception as e:
            logger.error(f"Auto-updater error: {e}")

        # 5 daqiqa kutish
        await asyncio.sleep(300)