import aiohttp
from config import SMM_API_URL, SMM_API_KEY, USD_TO_UZS, MARKUP_PERCENT

def usd_to_uzs_with_markup(rate_usd_per_1000: float) -> float:
    rate_per_1 = rate_usd_per_1000 / 1000
    uzs = rate_per_1 * USD_TO_UZS
    return round(uzs * (1 + MARKUP_PERCENT / 100), 4)

def calc_order_price(rate_usd_per_1000: float, quantity: int) -> float:
    per_item = usd_to_uzs_with_markup(rate_usd_per_1000)
    return round(per_item * quantity)

def price_per_1000_uzs(rate_usd_per_1000: float) -> int:
    return round(rate_usd_per_1000 / 1000 * USD_TO_UZS * (1 + MARKUP_PERCENT / 100) * 1000)

async def _post(payload: dict) -> dict | list:
    payload["key"] = SMM_API_KEY
    async with aiohttp.ClientSession() as session:
        async with session.post(SMM_API_URL, data=payload) as resp:
            return await resp.json(content_type=None)

async def get_balance_usd() -> float:
    result = await _post({"action": "balance"})
    try:
        return float(result.get("balance", 0))
    except Exception:
        return 0.0

async def place_order(service_id: int, link: str, quantity: int) -> dict:
    return await _post({
        "action": "add",
        "service": service_id,
        "link": link,
        "quantity": quantity
    })

async def get_order_status(order_id: int) -> dict:
    return await _post({"action": "status", "order": order_id})

# ─────────────────────────────────────────────────────────────
#  TELEGRAM HIZMATLARI — bo'limlarga ajratilgan
# ─────────────────────────────────────────────────────────────

TG_SECTIONS = {
    "👁 Ko'rishlar": [
        {
            "service": 15982,
            "name": "Ko'rishlar — Oddiy",
            "description": (
                "Post ko'rishlarini oshiradi.\n"
                "⚡ Tezkor — darhol boshlanadi.\n"
                "📌 Faqat ko'rish soni oshadi."
            ),
            "platform": "telegram",
            "rate": 0.0023,
            "min": 10,
            "max": 1000000,
        },
        {
            "service": 16926,
            "name": "Ko'rishlar — Barqaror",
            "description": (
                "Post ko'rishlarini oshiradi.\n"
                "✅ Har doim ishlaydi, tushib ketmaydi.\n"
                "📌 Uzoq muddatga ishonchli variant."
            ),
            "platform": "telegram",
            "rate": 0.0074,
            "min": 50,
            "max": 50000000,
        },
        {
            "service": 28478,
            "name": "Premium ko'rishlar",
            "description": (
                "Faqat Telegram Premium obunachilari tomonidan ko'rishlar.\n"
                "💎 Sifatli ko'rinish — kanalga ishonch oshadi.\n"
                "📌 Oddiy ko'rishdan qimmatroq, lekin premium sifat."
            ),
            "platform": "telegram",
            "rate": 0.0911,
            "min": 10,
            "max": 150000,
        },
    ],
    "😍 Reaksiyalar": [
        {
            "service": 28576,
            "name": "Aralash ijobiy reaksiyalar",
            "description": (
                "Postga turli ijobiy reaksiyalar qo'shiladi.\n"
                "👍🤩🎉🔥❤️🥰 — avtomatik aralash.\n"
                "📌 Qaysi reaksiya qo'shilishini tanlab bo'lmaydi."
            ),
            "platform": "telegram",
            "rate": 0.0186,
            "min": 10,
            "max": 1000000,
        },
        {
            "service": 23335,
            "name": "Faqat 👍 Like reaksiya",
            "description": (
                "Postga faqat 👍 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi, chiqib ketmaydi."
            ),
            "platform": "telegram",
            "rate": 0.0294,
            "min": 10,
            "max": 1000000,
        },
        {
            "service": 23338,
            "name": "Faqat ❤️ Yurak reaksiya",
            "description": (
                "Postga faqat ❤️ reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi, chiqib ketmaydi."
            ),
            "platform": "telegram",
            "rate": 0.0294,
            "min": 10,
            "max": 1000000,
        },
        {
            "service": 23339,
            "name": "Faqat 🔥 Olov reaksiya",
            "description": (
                "Postga faqat 🔥 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi, chiqib ketmaydi."
            ),
            "platform": "telegram",
            "rate": 0.0294,
            "min": 10,
            "max": 1000000,
        },
    ],
    "👥 Obunachilar": [
        {
            "service": 29541,
            "name": "Obunachi — 30 kunlik kafolat",
            "description": (
                "Real ko'rinishdagi akkauntlar kanalingizga qo'shiladi.\n"
                "🛡 30 kun ichida chiqib ketsa — bepul qayta to'ldiriladi.\n"
                "📌 Yangi kanallar uchun qulay narx."
            ),
            "platform": "telegram",
            "rate": 0.3108,
            "min": 10,
            "max": 1000000,
        },
        {
            "service": 29545,
            "name": "Obunachi — 1 yillik kafolat",
            "description": (
                "Real ko'rinishdagi akkauntlar kanalingizga qo'shiladi.\n"
                "🛡 365 kun ichida chiqib ketsa — bepul qayta to'ldiriladi.\n"
                "📌 Uzoq muddatli kanallar uchun tavsiya etiladi."
            ),
            "platform": "telegram",
            "rate": 0.5311,
            "min": 10,
            "max": 1000000,
        },
        {
            "service": 29546,
            "name": "Obunachi — Umrbod kafolat",
            "description": (
                "Real ko'rinishdagi akkauntlar kanalingizga qo'shiladi.\n"
                "🛡 Umrbod chiqib ketmaydi, doim refill qilinadi.\n"
                "📌 Eng ishonchli variant — bir marta to'lab xotirjam bo'ling."
            ),
            "platform": "telegram",
            "rate": 0.5763,
            "min": 10,
            "max": 1000000,
        },
    ],
}

# ─────────────────────────────────────────────────────────────
#  INSTAGRAM HIZMATLARI — bo'limlarga ajratilgan
# ─────────────────────────────────────────────────────────────

IG_SECTIONS = {
    "👁 Ko'rishlar": [
        {
            "service": 14065,
            "name": "Video / Reel / IGTV ko'rishlar",
            "description": (
                "Video, Reel yoki IGTV ko'rishlarini oshiradi.\n"
                "⚡ Juda tez — bir daqiqada boshlanadi.\n"
                "📌 Faqat ko'rish soni oshadi."
            ),
            "platform": "instagram",
            "rate": 0.0014,
            "min": 100,
            "max": 50000000,
        },
        {
            "service": 17649,
            "name": "Story ko'rishlar",
            "description": (
                "Story ko'rishlarini oshiradi.\n"
                "⚡ Tez yetkaziladi.\n"
                "📌 Faqat faol story larga ishlaydi."
            ),
            "platform": "instagram",
            "rate": 0.0028,
            "min": 10,
            "max": 100000,
        },
        {
            "service": 16452,
            "name": "Reel ko'rishlar",
            "description": (
                "Reel videolarning ko'rishlarini oshiradi.\n"
                "⚡ Eng tez va eng arzon variant.\n"
                "📌 Faqat Reel linki kiritilishi kerak."
            ),
            "platform": "instagram",
            "rate": 0.0011,
            "min": 100,
            "max": 2147483647,
        },
    ],
    "❤️ Layklar": [
        {
            "service": 13154,
            "name": "Layk — 30 kun kafolat",
            "description": (
                "Postga layklar qo'shiladi.\n"
                "🛡 30 kun ichida tushib ketsa — bepul qayta to'ldiriladi.\n"
                "✅ Barqaror, tushib ketmaydi."
            ),
            "platform": "instagram",
            "rate": 0.1432,
            "min": 10,
            "max": 500000,
        },
        {
            "service": 14808,
            "name": "Layk — Tez yetkazish",
            "description": (
                "Postga layklar qo'shiladi.\n"
                "⚡ Juda tez — bir necha daqiqada.\n"
                "📌 Kafolatsiz, biroz tushishi mumkin. Narxi qulay."
            ),
            "platform": "instagram",
            "rate": 0.1754,
            "min": 20,
            "max": 1000000,
        },
    ],
    "👤 Obunachilar": [
        {
            "service": 22042,
            "name": "Obunachi — Postlari bor akkauntlar",
            "description": (
                "Profiling real ko'rinishdagi akkauntlar tomonidan kuzatiladi.\n"
                "✅ Akkauntlarda postlar bor — ishonchli ko'rinadi.\n"
                "🛡 Tushib ketish darajasi juda past.\n"
                "📌 Sifatni ustun qo'ymoqchi bo'lsangiz shu."
            ),
            "platform": "instagram",
            "rate": 0.2645,
            "min": 100,
            "max": 100000,
        },
        {
            "service": 16350,
            "name": "Obunachi — Tez va arzon",
            "description": (
                "Profilingga tez obunachi qo'shiladi.\n"
                "⚡ Tez yetkaziladi, narxi qulay.\n"
                "📌 Biroz tushishi mumkin — kafolatsiz. Tezlik kerak bo'lsa shu."
            ),
            "platform": "instagram",
            "rate": 0.3431,
            "min": 100,
            "max": 500000,
        },
    ],
    "🔄 Ulashishlar": [
        {
            "service": 23928,
            "name": "Ulashishlar (Repost)",
            "description": (
                "Postingiz boshqa akkauntlar tomonidan ulashiladi.\n"
                "⚡ Juda tez — darhol boshlanadi.\n"
                "📌 Postni tarqatish va ko'proq odamga yetkazish uchun."
            ),
            "platform": "instagram",
            "rate": 0.0204,
            "min": 10,
            "max": 10000000,
        },
    ],
}

def get_tg_sections() -> dict:
    return TG_SECTIONS

def get_ig_sections() -> dict:
    return IG_SECTIONS

def get_tg_section_names() -> list:
    return list(TG_SECTIONS.keys())

def get_ig_section_names() -> list:
    return list(IG_SECTIONS.keys())

def get_section_services(platform: str, section: str) -> list:
    if platform == "telegram":
        return TG_SECTIONS.get(section, [])
    elif platform == "instagram":
        return IG_SECTIONS.get(section, [])
    return []

def find_service(service_id: int) -> dict | None:
    all_services = []
    for services in TG_SECTIONS.values():
        all_services.extend(services)
    for services in IG_SECTIONS.values():
        all_services.extend(services)
    for s in all_services:
        if s["service"] == service_id:
            return s
    return None