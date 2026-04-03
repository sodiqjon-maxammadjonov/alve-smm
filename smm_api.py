import aiohttp
import os
from config import SMM_API_URL, SMM_API_KEY, USD_TO_UZS

# ── Narx hisoblash ─────────────────────────────────────────────
# Qoida: arzon xizmatga ko'p markup, qimmatga kam markup.
# Agar xizmatda "markup" field bo'lsa — o'sha ishlatiladi.
# Yo'q bo'lsa auto_markup() qoidasi ishlaydi.
# .env dagi MARKUP_PERCENT faqat fallback sifatida saqlanadi.

def auto_markup(rate_usd_per_1000: float) -> float:
    """Rate asosida avtomatik markup foizi"""
    if rate_usd_per_1000 < 0.01:
        return 250.0   # 3.5x
    elif rate_usd_per_1000 < 0.1:
        return 180.0   # 2.8x
    elif rate_usd_per_1000 < 1.0:
        return 120.0   # 2.2x
    elif rate_usd_per_1000 < 5.0:
        return 70.0    # 1.7x
    else:
        return 40.0    # 1.4x


def get_markup(svc: dict) -> float:
    """Xizmat uchun markup olish (xizmat > env > auto)"""
    if "markup" in svc:
        return float(svc["markup"])
    env = os.getenv("MARKUP_PERCENT")
    if env:
        return float(env)
    return auto_markup(float(svc["rate"]))


def calc_price_uzs(rate_usd_per_1000: float, quantity: int, markup: float = None) -> int:
    if markup is None:
        markup = auto_markup(rate_usd_per_1000)
    per_item_uzs = (rate_usd_per_1000 / 1000) * USD_TO_UZS * (1 + markup / 100)
    return round(per_item_uzs * quantity)


def price_per_1000_uzs(rate_usd_per_1000: float, markup: float = None) -> int:
    if markup is None:
        markup = auto_markup(rate_usd_per_1000)
    return round((rate_usd_per_1000 / 1000) * USD_TO_UZS * (1 + markup / 100) * 1000)


def cost_price_uzs_per_item(rate_usd_per_1000: float) -> float:
    """Tan narxi (so'mda, markupsiz) — /discount uchun"""
    return (rate_usd_per_1000 / 1000) * USD_TO_UZS


# ── API ────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────────
#  XIZMATLAR
#
#  Har bir xizmat dict:
#    service     — Peakerr service ID
#    name        — Botda ko'rinadigan nom
#    description — Qisqa tavsif (1-2 qator)
#    rate        — USD per 1000 (Peakerr narxi, o'zgarmaydi)
#    min / max   — miqdor chegarasi
#    refill      — True: "♻️ Refill kafolatli" badge
#    bonus       — str: "15000 ta buyursangiz 25000 ta keladi" (ixtiyoriy)
#    markup      — ixtiyoriy float, yo'q bo'lsa auto_markup()
#
#  YANGI XIZMAT: bo'limga dict qo'shing
#  YANGI PLATFORMA: PLATFORMS ga yangi kalit qo'shing
# ──────────────────────────────────────────────────────────────

PLATFORMS = {

    # ════════════════════════════════════════════════════════
    "✈️ Telegram": {
        "👁 Ko'rishlar": [
            {
                "service": 15982,
                "name": "Ko'rishlar — Tez",
                "description": "⚡ Post ko'rishlarini darhol oshiradi.",
                "rate": 0.0023, "min": 10, "max": 1_000_000,
            },
            {
                "service": 16926,
                "name": "Ko'rishlar — Barqaror",
                "description": "✅ Tushib ketmaydigan, uzoq muddatli.",
                "rate": 0.0074, "min": 50, "max": 50_000_000,
                "refill": True,
            },
            {
                "service": 28478,
                "name": "Premium ko'rishlar 💎",
                "description": "Faqat Telegram Premium akkauntlardan.\n💎 Sifatli va ishonchli.",
                "rate": 0.0911, "min": 10, "max": 150_000,
            },
        ],
        "😍 Reaksiyalar": [
            {
                "service": 28576,
                "name": "Aralash ijobiy reaksiyalar",
                "description": "👍🤩🎉🔥❤️🥰 — avtomatik aralash.",
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
                "description": "Real ko'rinishdagi akkauntlar.",
                "rate": 0.3108, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 29545,
                "name": "Obunachi — 1 yil kafolat",
                "description": "Real ko'rinishdagi akkauntlar.\n🛡 365 kun kafolat.",
                "rate": 0.5311, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 29546,
                "name": "Obunachi — Umrbod kafolat ⭐",
                "description": "Eng ishonchli variant. 🛡 Umrbod.",
                "rate": 0.5763, "min": 10, "max": 1_000_000,
                "refill": True,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "📸 Instagram": {
        "👁 Ko'rishlar": [
            {
                "service": 16452,
                "name": "Reel ko'rishlar — Eng arzon",
                "description": "⚡ Tez va arzon Reel ko'rishlar.",
                "rate": 0.0011, "min": 100, "max": 2_147_483_647,
            },
            {
                "service": 14065,
                "name": "Video / Reel / IGTV ko'rishlar",
                "description": "⚡ Bir daqiqada boshlanadi.",
                "rate": 0.0014, "min": 100, "max": 50_000_000,
            },
            {
                "service": 17649,
                "name": "Story ko'rishlar",
                "description": "Faol story larga ko'rishlar.",
                "rate": 0.0028, "min": 10, "max": 100_000,
            },
        ],
        "❤️ Layklar": [
            {
                "service": 14808,
                "name": "Layk — Tez va arzon",
                "description": "⚡ Bir necha daqiqada. Qulay narx.",
                "rate": 0.1754, "min": 20, "max": 1_000_000,
            },
            {
                "service": 13154,
                "name": "Layk — 30 kun kafolat",
                "description": "🛡 30 kun ichida tushsa bepul to'ldiriladi.",
                "rate": 0.1432, "min": 10, "max": 500_000,
                "refill": True,
            },
        ],
        "👤 Obunachilar": [
            {
                "service": 16350,
                "name": "Obunachi — Tez Yetkazish",
                "description": "⚡ Tez yetkaziladi. Qulay narx.",
                "rate": 0.3431, "min": 100, "max": 500_000,
            },
            {
                "service": 22042,
                "name": "Obunachi — Real akauntlar",
                "description": "✅ Postlari bor real ko'rinishdagi akkauntlar.",
                "rate": 0.2645, "min": 100, "max": 100_000,
            },
        ],
        "🔄 Ulashishlar": [
            {
                "service": 23928,
                "name": "Ulashishlar (Repost)",
                "description": "⚡ Darhol boshlanadi.",
                "rate": 0.0204, "min": 10, "max": 10_000_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "🎵 TikTok": {
        "👁 Ko'rishlar": [
            {
                "service": 14090,
                "name": "Ko'rishlar — Real",
                "description": "⚡ Tez va real TikTok ko'rishlar.",
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
                "description": "Real akkauntlardan obunachilar.",
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
        "💾 Saqlashlar": [
            {
                "service": 10052,
                "name": "Saqlashlar (Save)",
                "description": "⚡ 0–15 daqiqada boshlanadi.",
                "rate": 1.84, "min": 10, "max": 10_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "▶️ YouTube": {
        "👁 Ko'rishlar": [
            {
                "service": 30749,
                "name": "Ko'rishlar — Arzon",
                "description": "1k–2k/kun tezlik.\n♻️ Umrbod refill kafolati.",
                "rate": 0.9492, "min": 100, "max": 2_500_000,
                "refill": True,
            },
            {
                "service": 30751,
                "name": "Ko'rishlar — O'rtacha",
                "description": "10k–50k/kun tezlik.\n♻️ Umrbod refill kafolati.",
                "rate": 0.8701, "min": 100, "max": 1_000_000_000,
                "refill": True,
            },
            {
                "service": 30727,
                "name": "Ko'rishlar — Tez ⚡",
                "description": "500k–1M/kun! Eng tez variant.\n♻️ Umrbod refill.",
                "rate": 1.13, "min": 1_000, "max": 2_147_483_647,
                "refill": True,
            },
        ],
        "👍 Layklar": [
            {
                "service": 22709,
                "name": "Layklar — Arzon",
                "description": "⚡ 0–15 daqiqada. 50K/kun tezlik.",
                "rate": 0.0791, "min": 10, "max": 10_000_000,
            },
            {
                "service": 18462,
                "name": "Layklar — O'rtacha",
                "description": "⚡ 0–15 daqiqada boshlanadi.",
                "rate": 0.113, "min": 10, "max": 1_000_000,
            },
            {
                "service": 24133,
                "name": "Layklar — Sifatli ♻️",
                "description": "HQ profillar. 30 kun refill kafolati.",
                "rate": 0.1695, "min": 10, "max": 80_000,
                "refill": True,
            },
        ],
        "🔔 Obunachi.": [
            {
                "service": 23304,
                "name": "Obunachi — Arzon",
                "description": "⚡ Tez, 10K/kun.",
                "rate": 0.1311, "min": 10, "max": 1_000_000,
            },
            {
                "service": 20415,
                "name": "Obunachi — O'rtacha",
                "description": "SuperInstant, 10K/kun.",
                "rate": 0.1808, "min": 10, "max": 100_000,
            },
            {
                "service": 18463,
                "name": "Obunachi — Sifatli",
                "description": "MQ profillar. Barqaror.",
                "rate": 0.339, "min": 100, "max": 500_000,
            },
        ],
        "💬 Izohlar": [
            {
                "service": 30515,
                "name": "Custom izohlar",
                "description": "Siz yozgan matnli izohlar qo'shiladi.",
                "rate": 0.565, "min": 5, "max": 1_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "📘 Facebook": {
        "👁 Ko'rishlar": [
            {
                "service": 19188,
                "name": "Video/Reel ko'rishlar — Arzon",
                "description": "⚡ 20k–30k/kun. Eng arzon variant.",
                "rate": 0.0283, "min": 100, "max": 100_000_000,
            },
            {
                "service": 16612,
                "name": "Video ko'rishlar — 3 soniya",
                "description": "100k–500k/kun tezlik.",
                "rate": 0.1356, "min": 100, "max": 1_000_000,
            },
            {
                "service": 16611,
                "name": "Video ko'rishlar — Monetizable",
                "description": "Monetizatsiya uchun yaroqli.",
                "rate": 0.2034, "min": 100, "max": 10_000_000,
            },
        ],
        "👍 Layklar": [
            {
                "service": 22683,
                "name": "Post layklari — Care 🥰",
                "description": "Care reaksiya, real profillar.",
                "rate": 0.0999, "min": 100, "max": 500_000,
            },
            {
                "service": 20927,
                "name": "Post layklari — O'rtacha",
                "description": "⚡ Tez, 10K/kun.",
                "rate": 0.6227, "min": 10, "max": 100_000,
            },
        ],
        "👥 Obunachilar": [
            {
                "service": 22713,
                "name": "Profil/Sahifa — Arzon",
                "description": "500k/kun tezlik. Non drop.",
                "rate": 0.2786, "min": 100, "max": 500_000,
            },
            {
                "service": 21993,
                "name": "Sahifa — O'rtacha",
                "description": "Non drop, 500K/kun.",
                "rate": 0.999, "min": 10, "max": 10_000_000,
            },
            {
                "service": 15614,
                "name": "Sahifa Like+Obunachi — Sifatli",
                "description": "Real profillar. 5k–10k/kun.",
                "rate": 0.904, "min": 100, "max": 150_000,
            },
        ],
    },
# ══════════════════════════════════════════════════════════════
# smm_api.py → PLATFORMS dictiga qo'shadigan yangi platformalar
# Facebook blokidan keyin, oxirgi kommentdan oldin joylashtiring
# ══════════════════════════════════════════════════════════════

    # ════════════════════════════════════════════════════════
    "🧵 Threads": {
        "👁 Ko'rishlar": [
            {
                "service": 30765,
                "name": "Ko'rishlar — Arzon",
                "description": "⚡ Darhol boshlanadi. Eng qulay narx.",
                "rate": 1.84, "min": 10, "max": 50_000,
            },
        ],
        "❤️ Layklar": [
            {
                "service": 30760,
                "name": "Layklar — Tez",
                "description": "⚡ Bir necha daqiqada boshlanadi.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
            {
                "service": 29559,
                "name": "Layklar — Organik HQ",
                "description": "✅ HQ akkauntlar. Past tushish.",
                "rate": 8.475, "min": 50, "max": 50_000,
            },
        ],
        "👤 Obunachilar": [
            {
                "service": 30759,
                "name": "Obunachilar — Tez",
                "description": "⚡ Tez yetkaziladi.",
                "rate": 5.53, "min": 10, "max": 5_000,
            },
            {
                "service": 29557,
                "name": "Obunachilar — Organik HQ",
                "description": "✅ Real ko'rinishdagi HQ akkauntlar.",
                "rate": 15.255, "min": 100, "max": 50_000,
            },
            {
                "service": 29558,
                "name": "Obunachilar — Organik + Refill ♻️",
                "description": "HQ akkauntlar. 🛡 Refill kafolatli.",
                "rate": 16.95, "min": 100, "max": 50_000,
                "refill": True,
            },
        ],
        "🔄 Repostlar": [
            {
                "service": 30761,
                "name": "Repostlar — Tez",
                "description": "⚡ Darhol boshlanadi.",
                "rate": 2.77, "min": 10, "max": 5_000,
            },
            {
                "service": 29561,
                "name": "Repostlar — Organik HQ",
                "description": "✅ HQ akkauntlar. Past tushish.",
                "rate": 20.34, "min": 50, "max": 50_000,
            },
        ],
        "💬 Izohlar": [
            {
                "service": 30764,
                "name": "Izohlar",
                "description": "Post izohlarini oshiradi.",
                "rate": 5.53, "min": 10, "max": 5_000,
            },
        ],
        "💾 Saqlashlar": [
            {
                "service": 30763,
                "name": "Saqlashlar (Save)",
                "description": "⚡ Darhol boshlanadi.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "🐦 Twitter / X": {
        "👁 Ko'rishlar": [
            {
                "service": 18322,
                "name": "Video ko'rishlar — Eng arzon",
                "description": "⚡ Tez. Eng past narx.",
                "rate": 0.0046, "min": 100, "max": 100_000_000,
            },
            {
                "service": 15010,
                "name": "Tweet ko'rishlar — Tez",
                "description": "⚡ 0–15 daqiqada boshlanadi.",
                "rate": 0.0133, "min": 100, "max": 5_000_000,
            },
            {
                "service": 29859,
                "name": "Ko'rishlar + Impression + Refill ♻️",
                "description": "Ko'rishlar, impressionlar va engagement.\n♻️ Refill kafolatli.",
                "rate": 0.0047, "min": 100, "max": 2_147_483_647,
                "refill": True,
            },
        ],
        "❤️ Layklar": [
            {
                "service": 2634,
                "name": "Layklar — Tez",
                "description": "⚡ Darhol boshlanadi. 3K/soat tezlik.",
                "rate": 4.2086, "min": 10, "max": 100_000,
            },
        ],
        "👤 Obunachilar": [
            {
                "service": 15026,
                "name": "Obunachilar — Tez",
                "description": "⚡ 0–15 daqiqada boshlanadi.",
                "rate": 1.3551, "min": 50, "max": 5_000,
            },
            {
                "service": 15030,
                "name": "Obunachilar — AQSh",
                "description": "🇺🇸 AQSh akkauntlari. Sifatli.",
                "rate": 3.3296, "min": 100, "max": 10_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "📌 Pinterest": {
        "👁 Ko'rishlar": [
            {
                "service": 30771,
                "name": "Ko'rishlar",
                "description": "⚡ Tez va arzon Pinterest ko'rishlar.",
                "rate": 1.84, "min": 10, "max": 50_000,
            },
        ],
        "❤️ Layklar": [
            {
                "service": 30767,
                "name": "Layklar",
                "description": "⚡ Darhol boshlanadi.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
        ],
        "👤 Obunachilar": [
            {
                "service": 30766,
                "name": "Obunachilar",
                "description": "Pinterest profilingizga obunachilar.",
                "rate": 5.52, "min": 10, "max": 5_000,
            },
        ],
        "🔄 Ulashishlar": [
            {
                "service": 30768,
                "name": "Ulashishlar (Share)",
                "description": "⚡ Darhol boshlanadi.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
        ],
        "💾 Saqlashlar": [
            {
                "service": 30769,
                "name": "Saqlashlar (Save / Pin)",
                "description": "⚡ Pinlaringizni saqlovchilar.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
        ],
        "💬 Izohlar": [
            {
                "service": 30770,
                "name": "Izohlar",
                "description": "Post izohlarini oshiradi.",
                "rate": 5.52, "min": 10, "max": 5_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    # "🎮 O'yinlar": { ...  },  ← kelajak uchun
    # ════════════════════════════════════════════════════════
    # "🎮 O'yinlar": {
    #     "💎 Donatlar": [
    #         {
    #             "service": XXXXX,
    #             "name": "PUBG — UC",
    #             "description": "...",
    #             "rate": 0.0, "min": 1, "max": 9999,
    #         },
    #     ],
    # },
}


def get_platform_names() -> list[str]:
    return list(PLATFORMS.keys())


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