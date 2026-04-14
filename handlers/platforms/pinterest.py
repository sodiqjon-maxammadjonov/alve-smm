"""
handlers/platforms/pinterest.py — Zendor SMM Bot
Pinterest platformasining xizmatlari.
"""

PINTEREST_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 30771,
            "name": "⚡ Ko'rishlar",
            "description": (
                "Pinterest pinlaringizga ko'rishlar qo'shiladi.\n"
                "Tez va arzon.\n"
                "⚠️ Kafolatsiz. Maks: 50 000 ta."
            ),
            "rate": 1.84, "min": 10, "max": 50_000,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 30767,
            "name": "⚡ Layklar",
            "description": (
                "Pinterest pinlaringizga layklar qo'shiladi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 30766,
            "name": "⚡ Obunachilar",
            "description": (
                "Pinterest profilingizga obunachilar qo'shiladi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 5.52, "min": 10, "max": 5_000,
        },
    ],

    "🔄 Ulashishlar": [
        {
            "service": 30768,
            "name": "⚡ Ulashishlar",
            "description": (
                "Pinterest pinlaringiz ulashish soni oshadi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    "💾 Saqlashlar": [
        {
            "service": 30769,
            "name": "⚡ Saqlashlar",
            "description": (
                "Pinterest pinlaringizni saqlovchilar soni oshadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    "💬 Izohlar": [
        {
            "service": 30770,
            "name": "⚡ Izohlar",
            "description": (
                "Pinterest postlaringizga izohlar qo'shiladi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 5.52, "min": 10, "max": 5_000,
        },
    ],
}
