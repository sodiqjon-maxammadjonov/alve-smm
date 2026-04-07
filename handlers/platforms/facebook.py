"""
handlers/platforms/facebook.py — Zendor SMM Bot
Facebook platformasining xizmatlari.
"""

FACEBOOK_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 28860,
            "name": "Ko'rishlar — Arzon ⚡",
            "description": (
                "0-5 daqiqada boshlanadi, kuniga 20-100 ming.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0028, "min": 100, "max": 10_000_000,
        },
        {
            "service": 29449,
            "name": "Ko'rishlar — Video/Reels ✅",
            "description": (
                "Video va Reels uchun ko'rishlar.\n"
                "0% tushish darajasi.\n"
                "⚠️ Kafolatsiz variant. Cheksiz miqdor."
            ),
            "rate": 0.0193, "min": 100, "max": 100_000_000,
        },
        {
            "service": 29450,
            "name": "Ko'rishlar — Video/Reels + Kafolatli ♻️",
            "description": (
                "Video va Reels uchun ko'rishlar.\n"
                "0% tushish darajasi.\n"
                "✅ Kafolatlangan — tushib ketsa to'ldiriladi."
            ),
            "rate": 0.0215, "min": 100, "max": 100_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 29577,
            "name": "Layklar — Sifatli ⚡",
            "description": (
                "Sifatli akkauntlardan layklar.\n"
                "Past tushish darajasi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.1300, "min": 10, "max": 1_000_000,
        },
        {
            "service": 29578,
            "name": "Layklar — Sifatli + Kafolatli ♻️",
            "description": (
                "Sifatli akkauntlardan layklar.\n"
                "Past tushish darajasi.\n"
                "✅ Kafolatlangan — tushib ketsa to'ldiriladi."
            ),
            "rate": 0.1356, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 29443,
            "name": "Obunachilar — Arzon ⚡",
            "description": (
                "Barcha turdagi sahifalarga obunachilar.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.1639, "min": 10, "max": 1_000_000,
        },
        {
            "service": 30130,
            "name": "Obunachilar — Sifatli ✅",
            "description": (
                "Sifatli akkauntlar, barcha turdagi sahifalar.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.1582, "min": 10, "max": 1_000_000,
        },
        {
            "service": 29444,
            "name": "Obunachilar — Kafolatli ♻️",
            "description": (
                "Barcha turdagi sahifalarga obunachilar.\n"
                "✅ Kafolatlangan — tushib ketsa to'ldiriladi."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 30131,
            "name": "Obunachilar — Sifatli + Kafolatli 🔥",
            "description": (
                "Sifatli akkauntlar, barcha turdagi sahifalar.\n"
                "🔥 Kafolatlangan — tushib ketsa to'ldiriladi.\n"
                "Eng ishonchli variant."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],
}