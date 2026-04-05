"""
handlers/platforms/pinterest.py — Zendor SMM Bot
Pinterest platformasining xizmatlari.
"""

PINTEREST_SERVICES: dict[str, list[dict]] = {

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
}
