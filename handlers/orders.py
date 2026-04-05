"""
handlers/orders.py — Zendor SMM Bot
Buyurtmalar holati ko'rish + background auto-updater (har 5 daqiqa).
"""

import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from database import get_user_orders, update_order_status, get_active_orders
from core.smm_api import get_order_status
from keyboards.menus import back_to_main
from core.constants import STATUS_UZ, STATUS_EMOJI, FINAL_STATUSES, DIVIDER
from config import ORDER_UPDATE_INTERVAL

router = Router()
logger = logging.getLogger(__name__)


async def _fetch_and_update(order: dict) -> str:
    """Bir buyurtma statusini API dan oladi va kerak bo'lsa yangilaydi."""
    smm_id    = order.get("smm_order_id")
    db_status = order.get("status", "Pending")

    if db_status in FINAL_STATUSES or not smm_id:
        return db_status

    try:
        data = await get_order_status(smm_id)
        if not data or "error" in data:
            return db_status
        new_status = data.get("status", db_status)
        if new_status != db_status:
            await update_order_status(smm_id, new_status)
            logger.info(f"Order #{smm_id}: {db_status} → {new_status}")
        return new_status
    except Exception as e:
        logger.warning(f"fetch_and_update error #{smm_id}: {e}")
        return db_status


# ── Foydalanuvchi: Buyurtmalarim ──────────────────────────────

@router.callback_query(F.data == "my_orders")
async def cb_my_orders(call: CallbackQuery):
    await call.answer()
    orders = await get_user_orders(call.from_user.id)

    if not orders:
        await call.message.edit_text(
            f"📋 <b>Buyurtmalarim</b>\n\n"
            "Sizda hali buyurtma yo'q.\n"
            "Xizmatlardan birini tanlang! 👇",
            reply_markup=back_to_main(),
            parse_mode="HTML",
        )
        return

    # Barcha aktiv buyurtmalarni parallel yangilaymiz
    statuses = await asyncio.gather(*[_fetch_and_update(o) for o in orders])

    lines = [f"📋 <b>Buyurtmalarim</b>  (oxirgi {len(orders)} ta)\n", DIVIDER]
    for o, status in zip(orders, statuses):
        emoji  = STATUS_EMOJI.get(status, "❓")
        st_txt = STATUS_UZ.get(status, f"❓ {status}")
        name   = (o.get("service_name") or "")[:28]
        lines.append(
            f"{emoji} <b>#{o.get('smm_order_id')}</b>  {name}\n"
            f"   🔢 {o.get('quantity', 0):,}  |  💰 {o.get('price_uzs', 0):,} so'm\n"
            f"   {st_txt}"
        )

    await call.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_main(),
        parse_mode="HTML",
    )


# ── Background Auto-Updater ───────────────────────────────────

async def auto_update_orders(bot: Bot) -> None:
    """
    Har ORDER_UPDATE_INTERVAL sekundda aktiv buyurtmalarni yangilaydi.
    Muhim o'zgarishlarda foydalanuvchiga avtomatik xabar yuboradi.
    """
    logger.info(f"Auto-updater ishga tushdi (interval: {ORDER_UPDATE_INTERVAL}s)")

    while True:
        try:
            orders = await get_active_orders(limit=100)
            if orders:
                logger.info(f"Auto-update: {len(orders)} ta aktiv buyurtma tekshirilmoqda")
                for order in orders:
                    await _process_order(bot, order)
                    await asyncio.sleep(0.35)   # API rate limit
        except Exception as e:
            logger.error(f"Auto-updater xato: {e}")

        await asyncio.sleep(ORDER_UPDATE_INTERVAL)


async def _process_order(bot: Bot, order: dict) -> None:
    """Bitta buyurtmani tekshirib, kerak bo'lsa foydalanuvchiga xabar yuboradi."""
    smm_id     = order.get("smm_order_id")
    old_status = order.get("status", "Pending")
    if not smm_id:
        return

    try:
        data = await get_order_status(smm_id)
        if not data or "error" in data:
            return

        new_status = data.get("status", old_status)
        if new_status == old_status:
            return

        await update_order_status(smm_id, new_status)
        logger.info(f"Auto #{smm_id}: {old_status} → {new_status}")

        # Muhim holatlarda foydalanuvchiga xabar
        if new_status in ("Completed", "Partial", "Canceled", "Cancelled"):
            msg = _status_change_message(new_status, order, smm_id, data)
            try:
                await bot.send_message(
                    chat_id=order["user_id"],
                    text=msg,
                    reply_markup=back_to_main(),
                    parse_mode="HTML",
                )
            except Exception:
                pass

    except Exception as e:
        logger.warning(f"_process_order #{smm_id}: {e}")


def _status_change_message(
    new_status: str, order: dict, smm_id: int, data: dict
) -> str:
    svc_name = (order.get("service_name") or "")[:30]
    qty      = order.get("quantity", 0)

    if new_status == "Completed":
        return (
            f"✅ <b>Buyurtma bajarildi!</b>\n\n"
            f"{DIVIDER}\n"
            f"🏷 {svc_name}\n"
            f"🔢 Miqdor: {qty:,}\n"
            f"🔖 ID: #{smm_id}\n"
            f"{DIVIDER}\n\n"
            "Xarid uchun rahmat! 🎉"
        )
    if new_status == "Partial":
        remains = data.get("remains", "?")
        return (
            f"⚠️ <b>Buyurtma qisman bajarildi</b>\n\n"
            f"{DIVIDER}\n"
            f"🏷 {svc_name}\n"
            f"🔢 Qolgan: {remains}\n"
            f"🔖 ID: #{smm_id}\n"
            f"{DIVIDER}"
        )
    return (
        f"❌ <b>Buyurtma bekor qilindi</b>\n\n"
        f"{DIVIDER}\n"
        f"🏷 {svc_name}\n"
        f"🔖 ID: #{smm_id}\n"
        f"{DIVIDER}\n\n"
        "Muammo bo'lsa admin bilan bog'laning."
    )
