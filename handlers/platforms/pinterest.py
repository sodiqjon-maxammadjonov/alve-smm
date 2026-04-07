"""
handlers/platforms/pinterest.py — Zendor SMM Bot
Pinterest platformasining xizmatlari.
"""

PINTEREST_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 30771,
            "name": "Ko'rishlar ⚡",
            "description": (
                "Pinterest pinlaringizga ko'rishlar.\n"
                "Tez va arzon.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 1.84, "min": 10, "max": 50_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 30767,
            "name": "Layklar ⚡",
            "description": (
                "Pinterest pinlaringizga layklar.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 30766,
            "name": "Obunachilar ⚡",
            "description": (
                "Pinterest profilingizga obunachilar.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 5.52, "min": 10, "max": 5_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 🔄 ULASHISHLAR
    # ────────────────────────────────────────────────────────────
    "🔄 Ulashishlar": [
        {
            "service": 30768,
            "name": "Ulashishlar ⚡",
            "description": (
                "Pinterest pinlaringiz ulashish soni oshadi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💾 SAQLASHLAR
    # ────────────────────────────────────────────────────────────
    "💾 Saqlashlar": [
        {
            "service": 30769,
            "name": "Saqlashlar (Pin) ⚡",
            "description": (
                "Pinterest pinlaringizni saqlovchilar soni oshadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💬 IZOHLAR
    # ────────────────────────────────────────────────────────────
    "💬 Izohlar": [
        {
            "service": 30770,
            "name": "Izohlar ⚡",
            "description": (
                "Pinterest postlaringizga izohlar.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 5.52, "min": 10, "max": 5_000,
        },
    ],
}