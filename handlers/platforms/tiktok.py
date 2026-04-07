"""
handlers/platforms/tiktok.py — Zendor SMM Bot
TikTok platformasining xizmatlari.
"""

TIKTOK_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 28676,
            "name": "Ko'rishlar — Arzon ⚡",
            "description": (
                "TikTok videolaringizga ko'rishlar.\n"
                "Tez boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0029, "min": 100, "max": 1_000_000,
        },
        {
            "service": 30086,
            "name": "Ko'rishlar — Sifatli ✅",
            "description": (
                "Sifatli akkauntlardan ko'rishlar.\n"
                "Cheksiz miqdorgacha.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0032, "min": 100, "max": 100_000_000,
        },
        {
            "service": 30575,
            "name": "Ko'rishlar — 30 kunlik kafolat ♻️",
            "description": (
                "Sifatli akkauntlardan ko'rishlar.\n"
                "✅ 30 kun ichida tushib ketsa, bepul to'ldiriladi.\n"
                "Cheksiz miqdorgacha."
            ),
            "rate": 0.0036, "min": 100, "max": 100_000_000,
            "refill": True,
        },
        {
            "service": 30087,
            "name": "Ko'rishlar — Sifatli + 30 kun kafolat 🔥",
            "description": (
                "Eng sifatli ko'rishlar.\n"
                "🔥 30 kun ichida tushib ketsa, bepul to'ldiriladi.\n"
                "Cheksiz miqdorgacha."
            ),
            "rate": 0.0036, "min": 100, "max": 100_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 26332,
            "name": "Layklar — Arzon ⚡",
            "description": (
                "0-5 daqiqada boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0102, "min": 10, "max": 2_100_000_000,
        },
        {
            "service": 26334,
            "name": "Layklar — Tez ✅",
            "description": (
                "Tez yetkaziladi, barqaror natija.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0125, "min": 10, "max": 2_100_000_000,
        },
        {
            "service": 29584,
            "name": "Layklar — 30 kunlik kafolat ♻️",
            "description": (
                "Layklar qo'shiladi, tushib ketsa to'ldiriladi.\n"
                "✅ 30 kun davomida kafolatlangan."
            ),
            "rate": 0.0147, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29502,
            "name": "Layklar — Sifatli + 30 kun kafolat 🔥",
            "description": (
                "Sifatli akkauntlardan layklar.\n"
                "🔥 30 kun davomida kafolatlangan. Max: 50 ming ta."
            ),
            "rate": 0.0153, "min": 10, "max": 50_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 28175,
            "name": "Obunachilar — Arzon ⚡",
            "description": (
                "Tez qo'shiladi, past tushish darajasi.\n"
                "✅ 10 kunlik kafolat bor."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29735,
            "name": "Obunachilar — Premium sifat ✅",
            "description": (
                "Past tushish darajasi, premium sifat.\n"
                "✅ 10 kunlik kafolat bor."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 25001,
            "name": "Obunachilar — Tez + Real 🔥",
            "description": (
                "Haqiqiy ko'rinishdagi sifatli akkauntlar.\n"
                "Darhol boshlanadi, juda tez.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.1582, "min": 10, "max": 5_000_000,
        },
        {
            "service": 25002,
            "name": "Obunachilar — Profil rasmi bor + Kafolatli 💎",
            "description": (
                "Profil rasmi bor haqiqiy ko'rinishdagi akkauntlar.\n"
                "💎 Kafolatlangan — tushib ketsa to'ldiriladi.\n"
                "Eng ishonchli va sifatli variant."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],
}