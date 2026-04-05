"""
handlers/platforms/youtube.py — Zendor SMM Bot
YouTube platformasining xizmatlari.
"""

YOUTUBE_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 20001,
            "name": "Ko'rishlar — Arzon ⚠️",
            "description": "⚡ Tez va arzon.\n⚠️ Kafolat yo'q.",
            "rate": 0.30, "min": 100, "max": 1_000_000,
        },
        {
            "service": 20002,
            "name": "Ko'rishlar — HQ ✅",
            "description": "HQ ko'rishlar, past tushish darajasi.",
            "rate": 1.20, "min": 500, "max": 500_000,
        },
    ],

    "👍 Layklar": [
        {
            "service": 20003,
            "name": "Layklar ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 1.50, "min": 50, "max": 50_000,
        },
    ],

    "🔔 Obunachi.": [
        {
            "service": 20004,
            "name": "Obunachilar — Arzon ⚠️",
            "description": "⚡ Tez.\n⚠️ Kafolat yo'q.",
            "rate": 3.00, "min": 100, "max": 50_000,
        },
    ],

    "💬 Izohlar": [
        {
            "service": 20005,
            "name": "Izohlar",
            "description": "Video izohlarini oshiradi.",
            "rate": 5.00, "min": 10, "max": 5_000,
        },
    ],
}
