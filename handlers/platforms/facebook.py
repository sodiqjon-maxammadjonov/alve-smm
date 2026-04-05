"""
handlers/platforms/facebook.py — Zendor SMM Bot
Facebook platformasining xizmatlari.
"""

FACEBOOK_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 25001,
            "name": "Video ko'rishlar ⚠️",
            "description": "⚡ Tez va arzon.\n⚠️ Kafolat yo'q.",
            "rate": 0.10, "min": 500, "max": 5_000_000,
        },
    ],

    "👍 Layklar": [
        {
            "service": 25002,
            "name": "Post layklari ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 1.20, "min": 100, "max": 50_000,
        },
    ],

    "👥 Obunachilar": [
        {
            "service": 25003,
            "name": "Sahifa obunachilar ⚠️",
            "description": "Sahifangizga obunachilar.\n⚠️ Kafolat yo'q.",
            "rate": 2.50, "min": 100, "max": 50_000,
        },
    ],
}
