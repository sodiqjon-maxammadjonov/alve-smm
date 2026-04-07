"""
handlers/platforms/twitter.py — Zendor SMM Bot
Twitter / X platformasining xizmatlari.
"""

TWITTER_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 18322,
            "name": "Ko'rishlar — Arzon ⚡",
            "description": (
                "Tweet va video ko'rishlar.\n"
                "Tez boshlanadi, eng past narx.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0046, "min": 100, "max": 100_000_000,
        },
        {
            "service": 29859,
            "name": "Ko'rishlar + Ta'sir + Kafolatli ♻️",
            "description": (
                "Ko'rishlar, ko'rishlar soni va faollik birga oshadi.\n"
                "✅ Kafolatlangan — tushib ketsa to'ldiriladi."
            ),
            "rate": 0.0047, "min": 100, "max": 2_147_483_647,
            "refill": True,
        },
        {
            "service": 15010,
            "name": "Ko'rishlar — Tez ✅",
            "description": (
                "0-15 daqiqada boshlanadi.\n"
                "Barqaror sifat, ishonchli variant."
            ),
            "rate": 0.0133, "min": 100, "max": 5_000_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 2634,
            "name": "Layklar — Tez ⚡",
            "description": (
                "Darhol boshlanadi, soatiga 3 ming tezlik.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 4.2086, "min": 10, "max": 100_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 15026,
            "name": "Obunachilar — Arzon ⚡",
            "description": (
                "0-15 daqiqada boshlanadi.\n"
                "⚠️ Kafolatsiz variant. Max: 5 ming ta."
            ),
            "rate": 1.3551, "min": 50, "max": 5_000,
        },
        {
            "service": 15030,
            "name": "Obunachilar — AQSh 🇺🇸 ✅",
            "description": (
                "Amerika Qo'shma Shtatlaridan sifatli akkauntlar.\n"
                "✅ Ishonchli va sifatli variant. Max: 10 ming ta."
            ),
            "rate": 3.3296, "min": 100, "max": 10_000,
        },
    ],
}