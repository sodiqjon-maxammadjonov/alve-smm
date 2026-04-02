import aiohttp
from config import SMM_API_URL, SMM_API_KEY, USD_TO_UZS, MARKUP_PERCENT


def usd_to_uzs_with_markup(rate_usd_per_1000: float) -> float:
    per_1 = rate_usd_per_1000 / 1000
    return round(per_1 * USD_TO_UZS * (1 + MARKUP_PERCENT / 100), 4)


def calc_order_price(rate_usd_per_1000: float, quantity: int) -> float:
    return round(usd_to_uzs_with_markup(rate_usd_per_1000) * quantity)


def price_per_1000_uzs(rate_usd_per_1000: float) -> int:
    return round(usd_to_uzs_with_markup(rate_usd_per_1000) * 1000)


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
    return await _post({"action": "add", "service": service_id, "link": link, "quantity": quantity})


async def get_order_status(order_id: int) -> dict:
    return await _post({"action": "status", "order": order_id})


# ──────────────────────────────────────────────────────────────
#  XIZMATLAR — har bir platforma bo'yicha bo'limlar
#  Yangi xizmat qo'shmoqchi bo'lsangiz:
#    1. Kerakli platformaning dict'iga yangi bo'lim yoki xizmat qo'shing
#    2. service — Peakerr service ID
#    3. rate    — USD per 1000 (Peakerr API dan olinadi)
#    4. min/max — minimal/maksimal miqdor
# ──────────────────────────────────────────────────────────────

PLATFORMS = {

    # ── ✈️ TELEGRAM ──────────────────────────────────────────────
    "✈️ Telegram": {
        "👁 Ko'rishlar": [
            {
                "service": 15982,
                "name": "Ko'rishlar — Tez yetkzish",
                "description": "Post ko'rishlarini tez oshiradi.\n⚡ Darhol boshlanadi.",
                "rate": 0.0023, "min": 10, "max": 1_000_000,
            },
            {
                "service": 16926,
                "name": "Ko'rishlar — Barqaror",
                "description": "Tushib ketmaydigan barqaror ko'rishlar.\n✅ Uzoq muddatga ishonchli.",
                "rate": 0.0074, "min": 50, "max": 50_000_000,
            },
            {
                "service": 28478,
                "name": "Premium ko'rishlar",
                "description": "Faqat Telegram Premium akkauntlardan ko'rishlar.\n💎 Sifatli va ishonchli.",
                "rate": 0.0911, "min": 10, "max": 150_000,
            },
        ],
        "😍 Reaksiyalar": [
            {
                "service": 28576,
                "name": "Aralash ijobiy reaksiyalar",
                "description": "👍🤩🎉🔥❤️🥰 — avtomatik aralash reaksiyalar.",
                "rate": 0.0186, "min": 10, "max": 1_000_000,
            },
            {
                "service": 23335,
                "name": "👍 Like reaksiya",
                "description": "Faqat 👍 reaksiya. ✅ Umrbod saqlanadi.",
                "rate": 0.0294, "min": 10, "max": 1_000_000,
            },
            {
                "service": 23338,
                "name": "❤️ Yurak reaksiya",
                "description": "Faqat ❤️ reaksiya. ✅ Umrbod saqlanadi.",
                "rate": 0.0294, "min": 10, "max": 1_000_000,
            },
            {
                "service": 23339,
                "name": "🔥 Olov reaksiya",
                "description": "Faqat 🔥 reaksiya. ✅ Umrbod saqlanadi.",
                "rate": 0.0294, "min": 10, "max": 1_000_000,
            },
        ],
        "👥 Obunachilar": [
            {
                "service": 29541,
                "name": "Obunachi — 30 kun kafolat",
                "description": "Real ko'rinishdagi akkauntlar.\n🛡 30 kun ichida chiqsa — bepul to'ldiriladi.",
                "rate": 0.3108, "min": 10, "max": 1_000_000,
            },
            {
                "service": 29545,
                "name": "Obunachi — 1 yil kafolat",
                "description": "Real ko'rinishdagi akkauntlar.\n🛡 365 kun kafolat.",
                "rate": 0.5311, "min": 10, "max": 1_000_000,
            },
            {
                "service": 29546,
                "name": "Obunachi — Umrbod kafolat",
                "description": "Eng ishonchli variant.\n🛡 Umrbod chiqib ketmaydi.",
                "rate": 0.5763, "min": 10, "max": 1_000_000,
            },
        ],
    },

    # ── 📸 INSTAGRAM ──────────────────────────────────────────────
    "📸 Instagram": {
        "👁 Ko'rishlar": [
            {
                "service": 14065,
                "name": "Video / Reel / IGTV ko'rishlar",
                "description": "⚡ Juda tez, bir daqiqada boshlanadi.",
                "rate": 0.0014, "min": 100, "max": 50_000_000,
            },
            {
                "service": 17649,
                "name": "Story ko'rishlar",
                "description": "Faol story larga ko'rishlar. ⚡ Tez yetkaziladi.",
                "rate": 0.0028, "min": 10, "max": 100_000,
            },
            {
                "service": 16452,
                "name": "Reel ko'rishlar — Eng arzon",
                "description": "⚡ Eng tez va eng arzon Reel ko'rishlar.",
                "rate": 0.0011, "min": 100, "max": 2_147_483_647,
            },
        ],
        "❤️ Layklar": [
            {
                "service": 13154,
                "name": "Layk real akkauntlardan",
                "description": "🛡 30 kun ichida tushsa bepul to'ldiriladi.",
                "rate": 0.1432, "min": 10, "max": 500_000,
            },
            {
                "service": 14808,
                "name": "Tez yetkazish",
                "description": "⚡ Bir necha daqiqada. Qulay narx.",
                "rate": 0.1754, "min": 20, "max": 1_000_000,
            },
        ],
        "👤 Obunachilar": [
            {
                "service": 22042,
                "name": "Obunachi — Postlari bor Real akkauntlar",
                "description": "Real ko'rinishdagi akkauntlar.\n✅ Ishonchli va barqaror.",
                "rate": 0.2645, "min": 100, "max": 100_000,
            },
            {
                "service": 16350,
                "name": "Obunachi — Tez Yetetkzish",
                "description": "⚡ Tez yetkaziladi, qulay narx.",
                "rate": 0.3431, "min": 100, "max": 500_000,
            },
        ],
        "🔄 Ulashishlar": [
            {
                "service": 23928,
                "name": "Ulashishlar (Repost)",
                "description": "⚡ Darhol boshlanadi. Postni tarqatish uchun.",
                "rate": 0.0204, "min": 10, "max": 10_000_000,
            },
        ],
    },

    # ── 🎵 TIKTOK ──────────────────────────────────────────────
    "🎵 TikTok": {
        "👁 Ko'rishlar": [
            {
                "service": 14090,
                "name": "Ko'rishlar — Real",
                "description": "⚡ Tez yetkaziladi, real akkauntlardan.",
                "rate": 3.58, "min": 10, "max": 10_000,
            },
        ],
        "❤️ Layklar": [
            {
                "service": 14091,
                "name": "Layklar — Real",
                "description": "⚡ Tez va sifatli layklar.",
                "rate": 2.68, "min": 10, "max": 10_000,
            },
        ],
        "👤 Obunachilar": [
            {
                "service": 2422,
                "name": "Obunachilar — Real",
                "description": "⚡ Real akkauntlardan obunachilar.",
                "rate": 7.16, "min": 10, "max": 10_000,
            },
        ],
        "🔄 Ulashishlar": [
            {
                "service": 2424,
                "name": "Ulashishlar",
                "description": "Post ulashishlarini oshiradi. ⚡ Tez.",
                "rate": 1.85, "min": 10, "max": 50_000,
            },
        ],
        "💬 Izohlar": [
            {
                "service": 2425,
                "name": "Ijobiy izohlar",
                "description": "Ijobiy va real ko'rinishdagi izohlar.",
                "rate": 8.06, "min": 5, "max": 50_000,
            },
        ],
    },

    # ── ▶️ YOUTUBE ──────────────────────────────────────────────
    # Qo'shmoqchi bo'lsangiz response.json dan YouTube service IDlarini toping
    # va quyidagi shablon bo'yicha qo'shing
    # "▶️ YouTube": {
    #     "👁 Ko'rishlar": [
    #         {
    #             "service": XXXXX,
    #             "name": "Ko'rishlar",
    #             "description": "...",
    #             "rate": 0.XX, "min": 100, "max": 1_000_000,
    #         },
    #     ],
    # },

    # ── 📘 FACEBOOK ──────────────────────────────────────────────
    # "📘 Facebook": {
    #     "👍 Layklar": [
    #         {
    #             "service": XXXXX,
    #             "name": "Sahifa laykları",
    #             "description": "...",
    #             "rate": 0.XX, "min": 100, "max": 50_000,
    #         },
    #     ],
    # },

    # ── 🎮 O'YINLAR (kelajakda) ──────────────────────────────────
    # "🎮 O'yinlar": {
    #     "💎 Donatlar": [
    #         {
    #             "service": XXXXX,
    #             "name": "O'yin nomi — Donat",
    #             "description": "...",
    #             "rate": 0.XX, "min": 1, "max": 9999,
    #         },
    #     ],
    # },
}


# ── API funksiyalari ──────────────────────────────────────────

def get_platform_names() -> list[str]:
    return list(PLATFORMS.keys())


def get_sections(platform: str) -> dict:
    return PLATFORMS.get(platform, {})


def get_section_names(platform: str) -> list[str]:
    return list(PLATFORMS.get(platform, {}).keys())


def get_section_services(platform: str, section: str) -> list:
    return PLATFORMS.get(platform, {}).get(section, [])


def find_service(service_id: int) -> dict | None:
    for platform_data in PLATFORMS.values():
        for services in platform_data.values():
            for s in services:
                if s["service"] == service_id:
                    return s
    return None