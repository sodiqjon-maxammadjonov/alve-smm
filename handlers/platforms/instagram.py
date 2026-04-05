"""
handlers/platforms/instagram.py — Zendor SMM Bot
Instagram platformasining xizmatlari.
"""

INSTAGRAM_SERVICES: dict[str, list[dict]] = {

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
            "name": "Layklar — HQ ✅",
            "description": "HQ akkauntlar. Past tushish darajasi.",
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
            "name": "Obunachilar — HQ ✅",
            "description": "Real ko'rinishdagi HQ akkauntlar.",
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
            "name": "Repostlar — HQ ✅",
            "description": "HQ akkauntlar. Past tushish.",
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
}
