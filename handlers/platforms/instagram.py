"""
handlers/platforms/instagram.py — Zendor SMM Bot
Instagram platformasining xizmatlari.
"""

INSTAGRAM_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 28841,
            "name": "Ko'rishlar — Arzon ⚡",
            "description": (
                "Video va Reels ko'rishlar.\n"
                "Darhol boshlanadi, juda tez.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0102, "min": 100, "max": 100_000,
        },
        {
            "service": 28850,
            "name": "Ko'rishlar — Sifatli ✅",
            "description": (
                "Sifatli akkauntlardan ko'rishlar.\n"
                "Tez boshlanadi, barqaror natija.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0102, "min": 500, "max": 50_000,
        },
        {
            "service": 27250,
            "name": "Ko'rishlar — 30 kunlik kafolat ♻️",
            "description": (
                "Video va Reels ko'rishlar.\n"
                "✅ 30 kun ichida tushib ketsa, bepul to'ldiriladi.\n"
                "Max: 100 million ta."
            ),
            "rate": 0.0102, "min": 100, "max": 100_000_000,
            "refill": True,
        },
        {
            "service": 27268,
            "name": "Post ko'rishlar — Kafolatli ♻️",
            "description": (
                "Oddiy postlar uchun ko'rishlar.\n"
                "✅ Kafolatlangan — tushib ketsa to'ldiriladi."
            ),
            "rate": 0.0113, "min": 100, "max": 5_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 16360,
            "name": "Layklar — Arzon ⚡",
            "description": (
                "Darhol boshlanadi, tez yetkaziladi.\n"
                "⚠️ Kafolatsiz — biroz tushishi mumkin."
            ),
            "rate": 0.1017, "min": 10, "max": 250_000,
        },
        {
            "service": 29160,
            "name": "Layklar — Real ko'rinishli ✅",
            "description": (
                "Real odamga o'xshash akkauntlardan layklar.\n"
                "Past tushish darajasi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.1017, "min": 10, "max": 200_000,
        },
        {
            "service": 29566,
            "name": "Layklar — 30 kunlik kafolat ♻️",
            "description": (
                "Layklar qo'shiladi, tushib ketsa to'ldiriladi.\n"
                "✅ 30 kun davomida kafolatlangan."
            ),
            "rate": 0.1029, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29567,
            "name": "Layklar — 60 kunlik kafolat ♻️",
            "description": (
                "Layklar qo'shiladi, tushib ketsa to'ldiriladi.\n"
                "✅ 60 kun davomida kafolatlangan."
            ),
            "rate": 0.1040, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 16286,
            "name": "Obunachilar — Arzon ⚡",
            "description": (
                "Darhol boshlanadi, soatiga 1-2 ming.\n"
                "⚠️ Kafolatsiz — vaqt o'tishi bilan tushishi mumkin."
            ),
            "rate": 0.524, "min": 10, "max": 1_000_000,
        },
        {
            "service": 30106,
            "name": "Obunachilar — Real + 60 kunlik kafolat ✅",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "✅ 60 kun ichida tushib ketsa, bepul to'ldiriladi.\n"
                "Max: 200 ming ta."
            ),
            "rate": 0.5198, "min": 10, "max": 200_000,
            "refill": True,
        },
        {
            "service": 30519,
            "name": "Obunachilar — App + 90 kunlik kafolat 🔥",
            "description": (
                "Mobil ilovali akkauntlar — past tushish darajasi.\n"
                "🔥 90 kun ichida tushib ketsa, bepul to'ldiriladi.\n"
                "Max: 5 million ta."
            ),
            "rate": 0.5311, "min": 10, "max": 5_000_000,
            "refill": True,
        },
        {
            "service": 29254,
            "name": "Obunachilar — AQSh 🇺🇸",
            "description": (
                "Amerika Qo'shma Shtatlari akkauntlari.\n"
                "✅ 60 kunlik sifat kafolati.\n"
                "Max: 25 ming ta."
            ),
            "rate": 0.5085, "min": 10, "max": 5_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💬 IZOHLAR
    # ────────────────────────────────────────────────────────────
    "💬 Izohlar": [
        {
            "service": 29484,
            "name": "Tasodifiy izohlar — Real ⚡",
            "description": (
                "100% haqiqiy akkauntlardan tasodifiy matnli izohlar.\n"
                "⚠️ Kafolatsiz variant. Max: 10 ming ta."
            ),
            "rate": 0.5085, "min": 10, "max": 10_000,
        },
        {
            "service": 29487,
            "name": "Tasodifiy izohlar — 30 kunlik kafolat ♻️",
            "description": (
                "100% haqiqiy akkauntlardan tasodifiy matnli izohlar.\n"
                "✅ 30 kun davomida kafolatlangan. Max: 100 ming ta."
            ),
            "rate": 0.6215, "min": 10, "max": 100_000,
            "refill": True,
        },
        {
            "service": 29491,
            "name": "O'z matningiz bilan izoh — Kafolatli ✍️",
            "description": (
                "Siz yozgan matn bilan izoh qoldiriladi.\n"
                "✅ 30 kun davomida kafolatlangan. Max: 100 ming ta."
            ),
            "rate": 0.8475, "min": 10, "max": 100_000,
            "refill": True,
            "custom_comments": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💾 SAQLASHLAR
    # ────────────────────────────────────────────────────────────
    "💾 Saqlashlar": [
        {
            "service": 18030,
            "name": "Saqlashlar — Arzon ⚡",
            "description": (
                "Postingiz saqlashlar soni oshadi.\n"
                "Darhol boshlanadi, kuniga 50 ming tezlik.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0031, "min": 10, "max": 200_000,
        },
        {
            "service": 6291,
            "name": "Saqlashlar — Sifatli ✅",
            "description": (
                "Sifatli akkauntlardan saqlashlar.\n"
                "Tez bajariladi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0034, "min": 10, "max": 50_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 🔄 ULASHISHLAR
    # ────────────────────────────────────────────────────────────
    "🔄 Ulashishlar": [
        {
            "service": 26633,
            "name": "Ulashishlar — Arzon ⚡",
            "description": (
                "Postingiz ulashishlar soni oshadi.\n"
                "Darhol boshlanadi, juda tez.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0091, "min": 10, "max": 2_100_000_000,
        },
        {
            "service": 26672,
            "name": "Ulashishlar — Sifatli ✅",
            "description": (
                "Sifatli akkauntlardan ulashishlar.\n"
                "Tez bajariladi, barqaror natija.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0091, "min": 10, "max": 10_000_000,
        },
    ],
}