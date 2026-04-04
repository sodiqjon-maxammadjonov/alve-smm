import aiohttp
import os
from config import SMM_API_URL, SMM_API_KEY, USD_TO_UZS

# ── Narx hisoblash ─────────────────────────────────────────────

def auto_markup(rate_usd_per_1000: float) -> float:
    if rate_usd_per_1000 < 0.01:
        return 250.0
    elif rate_usd_per_1000 < 0.1:
        return 180.0
    elif rate_usd_per_1000 < 1.0:
        return 120.0
    elif rate_usd_per_1000 < 5.0:
        return 70.0
    else:
        return 40.0


def get_markup(svc: dict) -> float:
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


async def place_order(
    service_id: int,
    link: str,
    quantity: int,
    comments: str | None = None,  # ✅ Custom Comments uchun
) -> dict:
    payload = {
        "action":   "add",
        "service":  service_id,
        "link":     link,
        "quantity": quantity,
    }
    # Custom Comments xizmatida har bir izoh yangi qatorda yuboriladi
    if comments:
        payload["comments"] = comments
    return await _post(payload)


async def get_order_status(order_id: int) -> dict:
    return await _post({"action": "status", "order": order_id})


# ──────────────────────────────────────────────────────────────
#  XIZMATLAR
#
#  ⚠️  MUHIM QOIDALAR:
#   1. COMING_SOON platformalar uchun: {}  (bo'sh dict)
#   2. COMING_SOON bo'limlar uchun:    []  (bo'sh list)
#   3. Hech qachon { ... } yoki [{  }] ishlatmang!
#
#  Har bir xizmat dict maydonlari:
#    service         — Peakerr service ID
#    name            — Botda ko'rinadigan nom
#    description     — Qisqa tavsif
#    rate            — USD per 1000
#    min / max       — miqdor chegarasi
#    refill          — True: refill kafolatli
#    markup          — ixtiyoriy float
#    link_override   — ixtiyoriy: alohida link so'rash (dict)
#    custom_comments — True: foydalanuvchidan izoh matni so'raladi
# ──────────────────────────────────────────────────────────────

PLATFORMS = {

    # ════════════════════════════════════════════════════════
    "✈️ Telegram": {

        "👁 Ko'rishlar": [
            {
                "service": 15982,
                "name": "Ko'rishlar — Eng arzon ⚠️",
                "description": "⚡ Ultra tez, 1M/kun tezlik.\n⚠️ Kafolatsiz — tushib ketishi mumkin.",
                "rate": 0.0023, "min": 10, "max": 1_000_000,
            },
            {
                "service": 16926,
                "name": "Ko'rishlar — Barqaror",
                "description": "✅ Tushib ketmaydigan. 1 post.\n⚡ Darhol boshlanadi.",
                "rate": 0.0074, "min": 50, "max": 100_000_000,
            },
            {
                # ✅ KANAL LINKI so'raydi
                "service": 15448,
                "name": "Ko'rishlar — So'nggi 5 post",
                "description": "📌 Oxirgi 5 postga bir vaqtda.\n✅ Non-drop, barqaror.",
                "rate": 0.0429, "min": 50, "max": 50_000_000,
                "link_override": {
                    "prompt": "📨 Kanal linkini yuboring:",
                    "hint": "Kanal linki yoki username",
                    "example": "https://t.me/kanalingiz  yoki  @kanalingiz",
                    "validate": "telegram_channel",
                },
            },
            {
                "service": 28478,
                "name": "Premium ko'rishlar 💎",
                "description": "💎 Faqat Telegram Premium akkauntlardan.\n✅ Eng sifatli va ishonchli.",
                "rate": 0.0911, "min": 10, "max": 150_000,
            },
        ],

        "😍 Reaksiyalar": [
            {
                "service": 18339,
                "name": "Aralash ijobiy reaksiyalar ⚠️",
                "description": "👍❤️🔥🎉🤩😁 — avtomatik aralash.\n⚠️ Kafolatsiz variant.",
                "rate": 0.0226, "min": 10, "max": 10_000_000,
            },
            {
                "service": 23335,
                "name": "👍 Like — Umrbod kafolat ♻️",
                "description": "Faqat 👍 reaksiya.\n✅ Umrbod saqlanadi.",
                "rate": 0.0294, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 23338,
                "name": "❤️ Yurak — Umrbod kafolat ♻️",
                "description": "Faqat ❤️ reaksiya.\n✅ Umrbod saqlanadi.",
                "rate": 0.0294, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 23339,
                "name": "🔥 Olov — Umrbod kafolat ♻️",
                "description": "Faqat 🔥 reaksiya.\n✅ Umrbod saqlanadi.",
                "rate": 0.0294, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 23345,
                "name": "🎉 Bayram — Umrbod kafolat ♻️",
                "description": "Faqat 🎉 reaksiya.\n✅ Umrbod saqlanadi.",
                "rate": 0.0294, "min": 10, "max": 1_000_000,
                "refill": True,
            },
        ],

        "👥 Obunachilar": [
            {
                "service": 29540,
                "name": "Obunachi — Arzon ⚠️",
                "description": "Real ko'rinishdagi akkauntlar. Tez.\n⚠️ Kafolatsiz — tushib ketishi mumkin.",
                "rate": 0.339, "min": 10, "max": 1_000_000,
            },
            {
                "service": 29541,
                "name": "Obunachi — 30 kun kafolat ♻️",
                "description": "Real akkauntlar.\n🛡 30 kun ichida tushsa bepul to'ldiriladi.",
                "rate": 0.3503, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 29545,
                "name": "Obunachi — 365 kun kafolat ♻️",
                "description": "Real akkauntlar.\n🛡 1 yil davomida kafolatlangan.",
                "rate": 0.5311, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 29546,
                "name": "Obunachi — Umrbod kafolat ⭐",
                "description": "Real akkauntlar.\n🛡 Umrbod kafolat — eng ishonchli variant.",
                "rate": 0.5763, "min": 10, "max": 1_000_000,
                "refill": True,
            },
        ],

        "💎 Premium A'zolar": [
            {
                "service": 29989,
                "name": "Premium — 7 kun",
                "description": "💎 Telegram Premium akkauntlar.\n✅ 7 kun non-drop kafolati.",
                "rate": 3.3335, "min": 10, "max": 50_000,
            },
            {
                "service": 29991,
                "name": "Premium — 15 kun",
                "description": "💎 Telegram Premium akkauntlar.\n✅ 15 kun non-drop kafolati.",
                "rate": 5.876, "min": 10, "max": 50_000,
            },
            {
                "service": 29994,
                "name": "Premium — 30 kun ⭐",
                "description": "💎 Telegram Premium akkauntlar.\n🛡 30 kun non-drop — eng mashhur variant.",
                "rate": 10.1135, "min": 10, "max": 50_000,
            },
            {
                "service": 29996,
                "name": "Premium — 90 kun 💎",
                "description": "💎 Telegram Premium akkauntlar.\n🛡 90 kun non-drop — uzoq muddatli kafolat.",
                "rate": 21.922, "min": 10, "max": 50_000,
            },
        ],

        "⭐️ Stars": [],
    },

    # ════════════════════════════════════════════════════════
    "📸 Instagram": {

        "👁 Ko'rishlar": [
            {
                "service": 16452,
                "name": "Reel ko'rishlar — Eng arzon ⚠️",
                "description": "⚡ Eng tez va arzon Reel ko'rishlar.\n⚠️ Kafolatsiz variant.",
                "rate": 0.0011, "min": 100, "max": 10_000_000,
            },
            {
                "service": 14065,
                "name": "Video / Reel / IGTV ko'rishlar",
                "description": "⚡ Bir daqiqada boshlanadi.\n✅ Video, Reel va IGTV uchun.",
                "rate": 0.0014, "min": 100, "max": 500_000_000,
            },
            {
                "service": 17649,
                "name": "Story ko'rishlar",
                "description": "📖 Faol story larga ko'rishlar.\n⚡ 0–30 daqiqada boshlanadi.",
                "rate": 0.0028, "min": 10, "max": 30_000,
            },
            {
                "service": 10566,
                "name": "Story + Impressions + Interaksiya",
                "description": "📊 Story ko'rishlar + profil tashrifi + interaksiya.\n✅ Keng qamrovli o'sish.",
                "rate": 0.0226, "min": 10, "max": 50_000,
            },
        ],

        "❤️ Layklar": [
            {
                "service": 30080,
                "name": "Layk — Eng arzon ⚠️",
                "description": "⚡ Tez va arzon. Non-drop.\n⚠️ LQ akkauntlar, kafolat yo'q.",
                "rate": 0.0565, "min": 100, "max": 5_000_000,
            },
            {
                "service": 30081,
                "name": "Layk — 30 kun kafolat ♻️",
                "description": "Non-drop. 20K/kun tezlik.\n🛡 30 kun refill kafolati.",
                "rate": 0.0577, "min": 100, "max": 5_000_000,
                "refill": True,
            },
            {
                "service": 30435,
                "name": "Layk — Real + 30 kun kafolat ♻️",
                "description": "✅ Postlari bor real akkauntlar.\n🛡 30 kun kafolat, 50K/kun tezlik.",
                "rate": 0.078, "min": 10, "max": 1_000_000,
                "refill": True,
            },
            {
                "service": 29442,
                "name": "Layk — Real + Umrbod kafolat ⭐",
                "description": "✅ Profil fotoli real akkauntlar.\n🛡 Umrbod refill — eng ishonchli.",
                "rate": 0.0899, "min": 10, "max": 5_000_000,
                "refill": True,
            },
        ],

        "👤 Obunachilar": [
            {
                "service": 30428,
                "name": "Obunachi — Eng arzon ⚠️",
                "description": "Real akkauntlar. 100K/kun tezlik.\n⚠️ 20–30% tushishi mumkin, kafolat yo'q.",
                "rate": 0.2114, "min": 100, "max": 1_000_000,
            },
            {
                "service": 30398,
                "name": "Obunachi — Low Drop",
                "description": "Old akkauntlar + postlari bor.\n📉 Past tushish darajasi, kafolatsiz.",
                "rate": 0.2577, "min": 100, "max": 100_000,
            },
            {
                "service": 30399,
                "name": "Obunachi — 30 kun kafolat ♻️",
                "description": "Old akkauntlar + postlari bor.\n🛡 30 kun davomida tushsa bepul to'ldiriladi.",
                "rate": 0.3164, "min": 100, "max": 100_000,
                "refill": True,
            },
            {
                "service": 30401,
                "name": "Obunachi — 90 kun kafolat ♻️",
                "description": "Old akkauntlar + postlari bor.\n🛡 90 kun kafolat — barqaror o'sish.",
                "rate": 0.3503, "min": 100, "max": 100_000,
                "refill": True,
            },
        ],

        "🔄 Ulashishlar": [
            {
                "service": 2423,
                "name": "Ulashishlar (Repost) ⚠️",
                "description": "⚡ Darhol boshlanadi, 50K/kun.\n⚠️ Kafolatsiz variant.",
                "rate": 0.0185, "min": 10, "max": 50_000,
            },
            {
                "service": 23928,
                "name": "Ulashishlar — Sifatli",
                "description": "⚡ Darhol boshlanadi.\n✅ Barqaror, past tushish.",
                "rate": 0.0204, "min": 10, "max": 10_000_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "🎵 TikTok": {

        "👁 Ko'rishlar": [
            {
                "service": 14090,
                "name": "Ko'rishlar — Real ⚠️",
                "description": "⚡ Tez va real TikTok ko'rishlar.\n⚠️ Kafolat yo'q.",
                "rate": 3.58, "min": 10, "max": 10_000,
            },
        ],

        "❤️ Layklar": [
            {
                "service": 14091,
                "name": "Layklar — Real ⚠️",
                "description": "⚡ Tez va sifatli layklar.\n⚠️ Kafolat yo'q.",
                "rate": 2.68, "min": 10, "max": 10_000,
            },
        ],

        "👤 Obunachilar": [
            {
                "service": 2422,
                "name": "Obunachilar — Real ⚠️",
                "description": "Real akkauntlardan obunachilar.\n⚠️ Kafolat yo'q.",
                "rate": 7.16, "min": 10, "max": 10_000,
            },
        ],

        "🔄 Ulashishlar": [
            {
                "service": 14566,
                "name": "Ulashishlar — Real",
                "description": "⚡ Darhol boshlanadi.\n✅ Real akkauntlar.",
                "rate": 1.79, "min": 10, "max": 10_000,
            },
            {
                "service": 2424,
                "name": "Ulashishlar — Ko'p",
                "description": "⚡ Tez. 10K/kun tezlik.",
                "rate": 1.85, "min": 10, "max": 50_000,
            },
        ],

        "💬 Izohlar": [
            {
                "service": 2425,
                "name": "Ijobiy izohlar",
                "description": "Ijobiy va real ko'rinishdagi izohlar.\n⚡ Tez yetkaziladi.",
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
                "service": 30751,
                "name": "Ko'rishlar — Arzon ♻️",
                "description": "10k–50k/kun tezlik.\n♻️ Umrbod refill kafolati.",
                "rate": 0.8701, "min": 100, "max": 1_000_000_000,
                "refill": True,
            },
            {
                "service": 30749,
                "name": "Ko'rishlar — Sekin, barqaror ♻️",
                "description": "1k–2k/kun tezlik. Tabiiy ko'rinadi.\n♻️ Umrbod refill kafolati.",
                "rate": 0.9492, "min": 100, "max": 2_500_000,
                "refill": True,
            },
            {
                "service": 30727,
                "name": "Ko'rishlar — Tez ⚡ ♻️",
                "description": "500k–1M/kun! Eng tez variant.\n♻️ Umrbod refill kafolati.",
                "rate": 1.13, "min": 1_000, "max": 2_147_483_647,
                "refill": True,
            },
        ],

        "👍 Layklar": [
            {
                "service": 22709,
                "name": "Layklar — Arzon ⚠️",
                "description": "⚡ 0–15 daqiqada. 50K/kun tezlik.\n⚠️ Kafolat yo'q.",
                "rate": 0.0791, "min": 10, "max": 10_000_000,
            },
            {
                "service": 18462,
                "name": "Layklar — O'rtacha",
                "description": "⚡ 0–15 daqiqada boshlanadi.\n✅ Barqaror sifat.",
                "rate": 0.113, "min": 10, "max": 1_000_000,
            },
            {
                "service": 24133,
                "name": "Layklar — HQ + 30 kun kafolat ♻️",
                "description": "HQ profillar. ⚡ Tez.\n🛡 30 kun refill kafolati.",
                "rate": 0.1695, "min": 10, "max": 80_000,
                "refill": True,
            },
        ],

        "🔔 Obunachi.": [
            {
                "service": 23304,
                "name": "Obunachi — Arzon ⚠️",
                "description": "⚡ Tez, 10K/kun.\n⚠️ Kafolat yo'q.",
                "rate": 0.1311, "min": 10, "max": 1_000_000,
            },
            {
                "service": 20415,
                "name": "Obunachi — O'rtacha",
                "description": "SuperInstant, 10K/kun.\n✅ Barqaror sifat.",
                "rate": 0.1808, "min": 10, "max": 100_000,
            },
            {
                "service": 18463,
                "name": "Obunachi — Sifatli ⭐",
                "description": "MQ profillar. Barqaror.\n✅ Eng ishonchli variant.",
                "rate": 0.339, "min": 100, "max": 500_000,
            },
        ],

        "💬 Izohlar": [
            {
                # ✅ Custom Comments — izoh matni so'raladi
                "service": 30515,
                "name": "Custom izohlar",
                "description": "✏️ Siz yozgan matnli izohlar.\n✅ Har bir izoh yangi qatorda yozing.",
                "rate": 0.791, "min": 5, "max": 1_000,
                "custom_comments": True,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "📘 Facebook": {

        "👁 Ko'rishlar": [
            {
                "service": 19188,
                "name": "Video/Reel ko'rishlar — Eng arzon ⚠️",
                "description": "⚡ 20k–30k/kun. Eng arzon variant.\n⚠️ Kafolat yo'q.",
                "rate": 0.0283, "min": 100, "max": 100_000_000,
            },
            {
                "service": 16612,
                "name": "Video ko'rishlar — 3 soniya",
                "description": "100k–500k/kun tezlik.\n✅ 3 soniyalik ko'rishlar.",
                "rate": 0.1356, "min": 100, "max": 1_000_000,
            },
            {
                "service": 16611,
                "name": "Video ko'rishlar — Monetizable ⭐",
                "description": "Monetizatsiya uchun yaroqli.\n✅ Sifatli ko'rishlar.",
                "rate": 0.2034, "min": 100, "max": 10_000_000,
            },
        ],

        "👍 Layklar": [
            {
                "service": 22683,
                "name": "Post layklari — Care 🥰",
                "description": "Care reaksiya, real profillar.\n⚡ Tez yetkaziladi.",
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
                "name": "Profil/Sahifa — Arzon ⚠️",
                "description": "500k/kun tezlik. Non drop.\n⚠️ Kafolat yo'q.",
                "rate": 0.2786, "min": 100, "max": 500_000,
            },
            {
                "service": 21993,
                "name": "Sahifa — O'rtacha",
                "description": "Non drop, 500K/kun.\n✅ Barqaror sifat.",
                "rate": 0.999, "min": 10, "max": 10_000_000,
            },
            {
                "service": 15614,
                "name": "Sahifa Like+Obunachi — Sifatli ⭐",
                "description": "Real profillar. 5k–10k/kun.\n✅ Eng ishonchli variant.",
                "rate": 0.904, "min": 100, "max": 150_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "🧵 Threads": {

        "👁 Ko'rishlar": [
            {
                "service": 30765,
                "name": "Ko'rishlar ⚠️",
                "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
                "rate": 1.84, "min": 10, "max": 50_000,
            },
        ],

        "❤️ Layklar": [
            {
                "service": 30760,
                "name": "Layklar — Tez ⚠️",
                "description": "⚡ Bir necha daqiqada boshlanadi.\n⚠️ Kafolat yo'q.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
            {
                "service": 29559,
                "name": "Layklar — HQ",
                "description": "✅ HQ akkauntlar. Past tushish darajasi.",
                "rate": 8.475, "min": 50, "max": 50_000,
            },
        ],

        "👤 Obunachilar": [
            {
                "service": 30759,
                "name": "Obunachilar — Tez ⚠️",
                "description": "⚡ Tez yetkaziladi.\n⚠️ Kafolat yo'q.",
                "rate": 5.53, "min": 10, "max": 5_000,
            },
            {
                "service": 29557,
                "name": "Obunachilar — HQ",
                "description": "✅ Real ko'rinishdagi HQ akkauntlar.",
                "rate": 15.255, "min": 100, "max": 50_000,
            },
            {
                "service": 29558,
                "name": "Obunachilar — HQ + Refill ♻️",
                "description": "HQ akkauntlar.\n🛡 Refill kafolati bor.",
                "rate": 16.95, "min": 100, "max": 50_000,
                "refill": True,
            },
        ],

        "🔄 Repostlar": [
            {
                "service": 30761,
                "name": "Repostlar — Tez ⚠️",
                "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
                "rate": 2.77, "min": 10, "max": 5_000,
            },
            {
                "service": 29561,
                "name": "Repostlar — HQ",
                "description": "✅ HQ akkauntlar. Past tushish.",
                "rate": 20.34, "min": 50, "max": 50_000,
            },
        ],

        "💬 Izohlar": [
            {
                "service": 30764,
                "name": "Izohlar",
                "description": "Post izohlarini oshiradi. ⚡ Tez.",
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
                "name": "Video ko'rishlar — Eng arzon ⚠️",
                "description": "⚡ Tez. Eng past narx.\n⚠️ Kafolat yo'q.",
                "rate": 0.0046, "min": 100, "max": 100_000_000,
            },
            {
                "service": 29859,
                "name": "Ko'rishlar + Impression ♻️",
                "description": "Ko'rishlar + impressionlar + engagement.\n♻️ Refill kafolatli.",
                "rate": 0.0047, "min": 100, "max": 2_147_483_647,
                "refill": True,
            },
            {
                "service": 15010,
                "name": "Tweet ko'rishlar — Tez",
                "description": "⚡ 0–15 daqiqada boshlanadi.\n✅ Barqaror sifat.",
                "rate": 0.0133, "min": 100, "max": 5_000_000,
            },
        ],

        "❤️ Layklar": [
            {
                "service": 2634,
                "name": "Layklar — Tez ⚠️",
                "description": "⚡ Darhol boshlanadi. 3K/soat tezlik.\n⚠️ Kafolat yo'q.",
                "rate": 4.2086, "min": 10, "max": 100_000,
            },
        ],

        "👤 Obunachilar": [
            {
                "service": 15026,
                "name": "Obunachilar — Tez ⚠️",
                "description": "⚡ 0–15 daqiqada boshlanadi.\n⚠️ Kafolat yo'q.",
                "rate": 1.3551, "min": 50, "max": 5_000,
            },
            {
                "service": 15030,
                "name": "Obunachilar — AQSh 🇺🇸",
                "description": "🇺🇸 AQSh akkauntlari. Sifatli.\n✅ Ishonchli variant.",
                "rate": 3.3296, "min": 100, "max": 10_000,
            },
        ],
    },

    # ════════════════════════════════════════════════════════
    "📌 Pinterest": {

        "👁 Ko'rishlar": [
            {
                "service": 30771,
                "name": "Ko'rishlar ⚠️",
                "description": "⚡ Tez va arzon Pinterest ko'rishlar.\n⚠️ Kafolat yo'q.",
                "rate": 1.84, "min": 10, "max": 50_000,
            },
        ],

        "❤️ Layklar": [
            {
                "service": 30767,
                "name": "Layklar ⚠️",
                "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
        ],

        "👤 Obunachilar": [
            {
                "service": 30766,
                "name": "Obunachilar ⚠️",
                "description": "Pinterest profilingizga obunachilar.\n⚠️ Kafolat yo'q.",
                "rate": 5.52, "min": 10, "max": 5_000,
            },
        ],

        "🔄 Ulashishlar": [
            {
                "service": 30768,
                "name": "Ulashishlar (Share) ⚠️",
                "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
        ],

        "💾 Saqlashlar": [
            {
                "service": 30769,
                "name": "Saqlashlar (Save / Pin) ⚠️",
                "description": "⚡ Pinlaringizni saqlovchilar.\n⚠️ Kafolat yo'q.",
                "rate": 1.84, "min": 10, "max": 5_000,
            },
        ],

        "💬 Izohlar": [
            {
                "service": 30770,
                "name": "Izohlar ⚠️",
                "description": "Post izohlarini oshiradi.\n⚠️ Kafolat yo'q.",
                "rate": 5.52, "min": 10, "max": 5_000,
            },
        ],
    },

    # ── COMING SOON ───────────────────────────────────────────
    "🎮 O'yinlar": {},
}


# ── Yordamchi funksiyalar ──────────────────────────────────────

def get_platform_names() -> list[str]:
    return list(PLATFORMS.keys())


def get_section_names(platform: str) -> list[str]:
    data = PLATFORMS.get(platform, {})
    if not isinstance(data, dict):
        return []
    return list(data.keys())


def get_section_services(platform: str, section: str) -> list:
    data = PLATFORMS.get(platform, {})
    if not isinstance(data, dict):
        return []
    services = data.get(section, [])
    return [s for s in services if isinstance(s, dict) and "service" in s]


def find_service(service_id: int) -> dict | None:
    for platform_data in PLATFORMS.values():
        if not isinstance(platform_data, dict):
            continue
        for services in platform_data.values():
            if not isinstance(services, list):
                continue
            for s in services:
                if not isinstance(s, dict):
                    continue
                if s.get("service") == service_id:
                    return s
    return None