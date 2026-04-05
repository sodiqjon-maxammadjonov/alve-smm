"""
handlers/platforms/tiktok.py — Zendor SMM Bot
TikTok platformasining xizmatlari.
"""

TIKTOK_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 10001,
            "name": "Ko'rishlar — Arzon ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 0.05, "min": 100, "max": 500_000,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 10002,
            "name": "Layklar — Tez ⚠️",
            "description": "⚡ Tez yetkaziladi.\n⚠️ Kafolat yo'q.",
            "rate": 0.12, "min": 50, "max": 100_000,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 10003,
            "name": "Obunachilar ⚠️",
            "description": "Real ko'rinishdagi akkauntlar.\n⚠️ Kafolat yo'q.",
            "rate": 0.85, "min": 50, "max": 50_000,
        },
    ],

    "🔄 Ulashishlar": [
        {
            "service": 10004,
            "name": "Ulashishlar ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 0.15, "min": 50, "max": 50_000,
        },
    ],

    "💬 Izohlar": [
        {
            "service": 10005,
            "name": "Izohlar",
            "description": "Video izohlarini oshiradi.",
            "rate": 0.50, "min": 10, "max": 5_000,
        },
    ],

    "💾 Saqlashlar": [
        {
            "service": 10006,
            "name": "Saqlashlar ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 0.10, "min": 50, "max": 50_000,
        },
    ],
}
