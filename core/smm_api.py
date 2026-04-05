"""
core/smm_api.py — Zendor SMM Bot
SMM API (Peakerr) klient + narx hisoblash + xizmatlar ro'yxati.

═══════════════════════════════════════════════════════════════
YANGI PLATFORMA QO'SHISH:
  1. handlers/platforms/ papkasiga yangi_platforma.py fayl oching
  2. PLATFORM_SERVICES dict ichiga {platform_nomi: {...}} qo'shing
  3. Ixtiyoriy: link_config.py ga link misoli qo'shing
═══════════════════════════════════════════════════════════════

YANGI XIZMAT QO'SHISH (mavjud platformaga):
  handlers/platforms/telegram.py (yoki boshqa platforma) fayliga
  tegishli bo'limga quyidagi dict ni qo'shing:
  {
      "service":  <Peakerr service ID>,
      "name":     "Ko'rinadigan nom",
      "description": "Qisqa tavsif",
      "rate":     <USD per 1000>,
      "min":      <minimal miqdor>,
      "max":      <maksimal miqdor>,
      # Ixtiyoriy:
      "refill":        True,           # refill kafolat bormi?
      "markup":        150.0,          # bu xizmat uchun alohida markup %
      "link_override": {...},          # alohida link so'rash
      "custom_comments": True,         # foydalanuvchidan izoh matni so'rash
  }
"""

import aiohttp
import logging
from config import SMM_API_URL, SMM_API_KEY, USD_TO_UZS, MARKUP_PERCENT

# Platform fayllarini import qilish
from handlers.platforms.telegram   import TELEGRAM_SERVICES
from handlers.platforms.instagram  import INSTAGRAM_SERVICES
from handlers.platforms.tiktok     import TIKTOK_SERVICES
from handlers.platforms.youtube    import YOUTUBE_SERVICES
from handlers.platforms.facebook   import FACEBOOK_SERVICES
from handlers.platforms.twitter    import TWITTER_SERVICES
from handlers.platforms.threads    import THREADS_SERVICES
from handlers.platforms.pinterest  import PINTEREST_SERVICES

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
#  PLATFORMALAR — Barcha xizmatlar shu yerda birlashadi
#  Yangi platforma qo'shish: import + PLATFORM_SERVICES ga qo'shing
# ═══════════════════════════════════════════════════════════════

PLATFORM_SERVICES: dict[str, dict | None] = {
    "✈️ Telegram":    TELEGRAM_SERVICES,
    "📸 Instagram":   INSTAGRAM_SERVICES,
    "🎵 TikTok":      TIKTOK_SERVICES,
    "▶️ YouTube":     YOUTUBE_SERVICES,
    "📘 Facebook":    FACEBOOK_SERVICES,
    "🐦 Twitter / X": TWITTER_SERVICES,
    "🧵 Threads":     THREADS_SERVICES,
    "📌 Pinterest":   PINTEREST_SERVICES,
    # COMING SOON — None yoki {} bo'lsa tugma "tez orada" ko'rsatadi
    "🎮 O'yinlar":    None,
}

# ═══════════════════════════════════════════════════════════════
#  NARX HISOBLASH
# ═══════════════════════════════════════════════════════════════

def auto_markup(rate_usd_per_1000: float) -> float:
    """
    Narxga qarab avtomatik markup foizi.
    Arzon xizmatga ko'p markup, qimmatga kam.
    """
    if rate_usd_per_1000 < 0.01:  return 250.0
    if rate_usd_per_1000 < 0.1:   return 180.0
    if rate_usd_per_1000 < 1.0:   return 120.0
    if rate_usd_per_1000 < 5.0:   return  70.0
    return 40.0


def get_markup(svc: dict) -> float:
    """Xizmat uchun markup foizini aniqlaydi (prioritet: svc > env > auto)."""
    if "markup" in svc:
        return float(svc["markup"])
    if MARKUP_PERCENT:
        return float(MARKUP_PERCENT)
    return auto_markup(float(svc["rate"]))


def calc_price_uzs(rate_usd_per_1000: float, quantity: int, markup: float | None = None) -> int:
    """Berilgan miqdor uchun umumiy narx (so'm)."""
    if markup is None:
        markup = auto_markup(rate_usd_per_1000)
    per_item = (rate_usd_per_1000 / 1000) * USD_TO_UZS * (1 + markup / 100)
    return round(per_item * quantity)


def price_per_1000_uzs(rate_usd_per_1000: float, markup: float | None = None) -> int:
    """1000 ta uchun narx (so'm) — xizmatlar ro'yxatida ko'rsatish uchun."""
    if markup is None:
        markup = auto_markup(rate_usd_per_1000)
    return round((rate_usd_per_1000 / 1000) * USD_TO_UZS * (1 + markup / 100) * 1000)


def cost_price_uzs_per_item(rate_usd_per_1000: float) -> float:
    """Tannarx — chegirma hisoblash uchun."""
    return (rate_usd_per_1000 / 1000) * USD_TO_UZS


# ═══════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR — Platformalar/Xizmatlar
# ═══════════════════════════════════════════════════════════════

def get_platform_names() -> list[str]:
    return list(PLATFORM_SERVICES.keys())


def is_coming_soon(platform: str) -> bool:
    data = PLATFORM_SERVICES.get(platform)
    return data is None or data == {}


def get_section_names(platform: str) -> list[str]:
    data = PLATFORM_SERVICES.get(platform)
    if not isinstance(data, dict):
        return []
    return list(data.keys())


def get_section_services(platform: str, section: str) -> list[dict]:
    data = PLATFORM_SERVICES.get(platform)
    if not isinstance(data, dict):
        return []
    svcs = data.get(section, [])
    return [s for s in svcs if isinstance(s, dict) and "service" in s]


def find_service(service_id: int) -> dict | None:
    """service ID bo'yicha xizmatni topadi."""
    for platform_data in PLATFORM_SERVICES.values():
        if not isinstance(platform_data, dict):
            continue
        for svcs in platform_data.values():
            if not isinstance(svcs, list):
                continue
            for s in svcs:
                if isinstance(s, dict) and s.get("service") == service_id:
                    return s
    return None


def find_platform_section(service_id: int) -> tuple[str, str]:
    """service ID bo'yicha platform va section nomini topadi."""
    for platform, platform_data in PLATFORM_SERVICES.items():
        if not isinstance(platform_data, dict):
            continue
        for section, svcs in platform_data.items():
            if not isinstance(svcs, list):
                continue
            for s in svcs:
                if isinstance(s, dict) and s.get("service") == service_id:
                    return platform, section
    return "", ""


# ═══════════════════════════════════════════════════════════════
#  SMM API SO'ROVLAR
# ═══════════════════════════════════════════════════════════════

async def _api_post(payload: dict) -> dict:
    """Asosiy API so'rov yuboruvchi."""
    payload["key"] = SMM_API_KEY
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SMM_API_URL, data=payload, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                return await resp.json(content_type=None)
    except Exception as e:
        logger.error(f"SMM API error: {e}")
        return {"error": str(e)}


async def get_smm_balance() -> float:
    """SMM panel hisobidagi USD balansi."""
    result = await _api_post({"action": "balance"})
    try:
        return float(result.get("balance", 0))
    except Exception:
        return 0.0


async def place_order(
    service_id: int,
    link: str,
    quantity: int,
    comments: str | None = None,
) -> dict:
    """
    Yangi buyurtma berish.
    comments — Custom Comments xizmatida foydalanuvchi yozgan izohlar.
    """
    payload = {
        "action":   "add",
        "service":  service_id,
        "link":     link,
        "quantity": quantity,
    }
    if comments:
        payload["comments"] = comments
    return await _api_post(payload)


async def get_order_status(order_id: int) -> dict:
    """Buyurtma holati."""
    return await _api_post({"action": "status", "order": order_id})
