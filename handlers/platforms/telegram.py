"""
handlers/platforms/telegram.py — Zendor SMM Bot
Telegram platformasining barcha xizmatlari.
"""

TELEGRAM_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 15982,
            "name": "Ko'rishlar — Arzon ⚡",
            "description": (
                "1 ta postga ko'rishlar qo'shiladi.\n"
                "Juda tez — kuniga 1 milliongacha.\n"
                "⚠️ Kafolatsiz, tushib ketishi mumkin."
            ),
            "rate": 0.0023, "min": 10, "max": 1_000_000,
        },
        {
            "service": 16926,
            "name": "Ko'rishlar — Barqaror ✅",
            "description": (
                "1 ta postga ko'rishlar qo'shiladi.\n"
                "Barqaror — tushib ketmaydi.\n"
                "✅ Ishonchli va sifatli variant."
            ),
            "rate": 0.0074, "min": 50, "max": 100_000_000,
        },
        {
            "service": 15448,
            "name": "Ko'rishlar — So'nggi 5 post 🔥",
            "description": (
                "Kanalingizdagi oxirgi 5 ta postga\n"
                "bir vaqtning o'zida ko'rishlar qo'shiladi.\n"
                "✅ Tushib ketmaydi, barqaror."
            ),
            "rate": 0.0429, "min": 50, "max": 50_000_000,
            "link_override": {
                "prompt": "📨 Kanal linkini yuboring:",
                "hint": "Kanal linki yoki username",
                "example": "https://t.me/kanalingiz  yoki  @kanalingiz",
                "validate": "telegram_channel",
            },
        },
        {
            "service": 28478,
            "name": "Ko'rishlar — Premium akkauntlar 💎",
            "description": (
                "Faqat Telegram Premium obunachili\n"
                "haqiqiy akkauntlardan ko'rishlar keladi.\n"
                "💎 Eng yuqori sifat va ishonchlilik."
            ),
            "rate": 0.0911, "min": 10, "max": 150_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 😍 REAKSIYALAR
    # ────────────────────────────────────────────────────────────
    "😍 Reaksiyalar": [
        {
            "service": 18339,
            "name": "Aralash reaksiyalar — Arzon ⚡",
            "description": (
                "👍❤️🔥🎉🤩😁 — avtomatik aralash reaksiyalar.\n"
                "Tez va arzon variant.\n"
                "⚠️ Kafolatsiz."
            ),
            "rate": 0.0226, "min": 10, "max": 10_000_000,
        },
        {
            "service": 23335,
            "name": "👍 Like reaksiya — Umrbod ♻️",
            "description": (
                "Postingizga faqat 👍 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi, hech qachon tushib ketmaydi."
            ),
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23338,
            "name": "❤️ Yurak reaksiya — Umrbod ♻️",
            "description": (
                "Postingizga faqat ❤️ reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi, hech qachon tushib ketmaydi."
            ),
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23339,
            "name": "🔥 Olov reaksiya — Umrbod ♻️",
            "description": (
                "Postingizga faqat 🔥 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi, hech qachon tushib ketmaydi."
            ),
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23345,
            "name": "🎉 Bayram reaksiya — Umrbod ♻️",
            "description": (
                "Postingizga faqat 🎉 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi, hech qachon tushib ketmaydi."
            ),
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👥 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👥 Obunachilar": [
        {
            "service": 29540,
            "name": "Obunachilar — Arzon ⚡",
            "description": (
                "Real ko'rinishdagi akkauntlar tez qo'shiladi.\n"
                "⚠️ Kafolatsiz — vaqt o'tishi bilan biroz tushishi mumkin."
            ),
            "rate": 0.339, "min": 10, "max": 1_000_000,
        },
        {
            "service": 29541,
            "name": "Obunachilar — 30 kunlik kafolat ✅",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "✅ 30 kun ichida tushib ketsa, bepul to'ldiriladi."
            ),
            "rate": 0.3503, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29545,
            "name": "Obunachilar — 1 yillik kafolat 🛡",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "🛡 1 yil davomida tushib ketsa, bepul to'ldiriladi."
            ),
            "rate": 0.5311, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29546,
            "name": "Obunachilar — Umrbod kafolat ⭐",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "⭐ Umrbod kafolat — hech qachon tushib ketmaydi.\n"
                "Eng ishonchli va uzoq muddatli variant."
            ),
            "rate": 0.5763, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💎 PREMIUM A'ZOLAR
    # ────────────────────────────────────────────────────────────
    "💎 Premium A'zolar": [
        {
            "service": 29989,
            "name": "Premium a'zolar — 7 kunlik kafolat",
            "description": (
                "Telegram Premium obunali haqiqiy akkauntlar.\n"
                "Kanalingizga obunachi bo'ladi.\n"
                "✅ 7 kun tushib ketmaydi."
            ),
            "rate": 3.3335, "min": 10, "max": 50_000,
        },
        {
            "service": 29991,
            "name": "Premium a'zolar — 15 kunlik kafolat ✅",
            "description": (
                "Telegram Premium obunali haqiqiy akkauntlar.\n"
                "Kanalingizga obunachi bo'ladi.\n"
                "✅ 15 kun tushib ketmaydi."
            ),
            "rate": 5.876, "min": 10, "max": 50_000,
        },
        {
            "service": 29994,
            "name": "Premium a'zolar — 30 kunlik kafolat 🔥",
            "description": (
                "Telegram Premium obunali haqiqiy akkauntlar.\n"
                "Kanalingizga obunachi bo'ladi.\n"
                "🔥 30 kun tushib ketmaydi — eng mashhur variant."
            ),
            "rate": 10.1135, "min": 10, "max": 50_000,
        },
    ],
}