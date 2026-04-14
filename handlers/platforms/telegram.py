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
            "name": "⚡ Arzon ko'rishlar — darhol",
            "description": (
                "1 ta postingizga ko'rishlar qo'shiladi.\n"
                "Darhol boshlanadi — kuniga 1 000 000 gacha.\n"
                "💡 Arzon narx = bot ko'rishlar ishlatiladi.\n"
                # "⚠️ Kafolatsiz: vaqt o'tishi bilan biroz kamayishi mumkin."
            ),
            "rate": 0.0023, "min": 10, "max": 1_000_000,
        },
        {
            "service": 16926,
            "name": "✅ Barqaror ko'rishlar ",
            "description": (
                "1 ta postingizga ko'rishlar qo'shiladi.\n"
                "Sifatli manbalardan — uzoq vaqt saqlanadi.\n"
                "✅ Ishonchli va barqaror variant. Maks: 100 000 000 ta."
            ),
            "rate": 0.0074, "min": 50, "max": 100_000_000,
        },
        {
            "service": 15448,
            "name": "🔥 So'nggi 5 postga bir vaqtda",
            "description": (
                "Kanalingizdagi oxirgi 5 ta postga\n"
                "bir vaqtning o'zida ko'rishlar qo'shiladi.\n"
                "✅ Barqaror, tushib ketmaydi. Maks: 50 000 000 ta."
            ),
            "rate": 0.0429, "min": 50, "max": 50_000_000,
            "link_override": {
                "prompt": "📨 Kanal linkini yuboring (post emas, kanal):",
                "hint": "Kanal linki yoki username",
                "example": "https://t.me/kanalingiz  yoki  @kanalingiz",
                "validate": "telegram_channel",
            },
        },
        {
            "service": 28478,
            "name": "💎 Premium akkauntlardan ko'rishlar",
            "description": (
                "Faqat Telegram Premium obunali\n"
                "haqiqiy akkauntlardan ko'rishlar keladi.\n"
                "💎 Eng yuqori sifat. Maks: 150 000 ta."
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
            "name": "⚡ Aralash reaksiyalar — arzon",
            "description": (
                "👍❤️🔥🎉🤩😁 — avtomatik aralash reaksiyalar qo'shiladi.\n"
                "Darhol boshlanadi, juda tez.\n"
                "⚠️ Kafolatsiz variant. Maks: 10 000 000 ta."
            ),
            "rate": 0.0226, "min": 10, "max": 10_000_000,
        },
        {
            "service": 23335,
            "name": "👍 Faqat LIKE — umrbod kafolat ♻️",
            "description": (
                "Postingizga faqat 👍 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi — hech qachon tushib ketmaydi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23338,
            "name": "❤️ Faqat YURAK — umrbod kafolat ♻️",
            "description": (
                "Postingizga faqat ❤️ reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi — hech qachon tushib ketmaydi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23339,
            "name": "🔥 Faqat OLOV — umrbod kafolat ♻️",
            "description": (
                "Postingizga faqat 🔥 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi — hech qachon tushib ketmaydi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23345,
            "name": "🎉 Faqat BAYRAM — umrbod kafolat ♻️",
            "description": (
                "Postingizga faqat 🎉 reaksiya qo'shiladi.\n"
                "✅ Umrbod saqlanadi — hech qachon tushib ketmaydi.\n"
                "Maks: 1 000 000 ta."
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
            "name": "⚡ Arzon obunachilar — tez",
            "description": (
                "Real ko'rinishdagi akkauntlar tez qo'shiladi.\n"
                "💡 Arzon narx bo'lgani uchun bir qismi keyinchalik tushishi mumkin.\n"
                "⚠️ Kafolatsiz — pul qaytarilmaydi, lekin juda katta\n"
                "   kamayish bo'lsa admin bilan bog'laning."
            ),
            "rate": 0.339, "min": 10, "max": 1_000_000,
        },
        {
            "service": 29541,
            "name": "♻️ Obunachilar + 30 kun kafolat",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "✅ 30 kun ichida tushib ketsa — bepul to'ldirib beriladi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.3503, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29545,
            "name": "🛡 Obunachilar + 1 yil kafolat",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "🛡 Butun 1 yil davomida tushsa — bepul to'ldirib beriladi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.5311, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29546,
            "name": "⭐ Obunachilar — UMRBOD kafolat",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "⭐ Umrbod kafolat — hech qachon tushib ketmaydi.\n"
                "Eng ishonchli va uzoq muddatli variant. Maks: 1 000 000 ta."
            ),
            "rate": 0.5763, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💎 PREMIUM A'ZOLAR
    # ────────────────────────────────────────────────────────────
    "💎 Premium a'zolar": [
        {
            "service": 29989,
            "name": "💎 Premium a'zolar — 7 kun kafolat",
            "description": (
                "Telegram Premium obunali haqiqiy akkauntlar\n"
                "kanalingizga obunachi bo'ladi.\n"
                "✅ 7 kun ichida tushsa — almashtiradi. Maks: 50 000 ta."
            ),
            "rate": 3.3335, "min": 10, "max": 50_000,
        },
        {
            "service": 29991,
            "name": "💎 Premium a'zolar — 15 kun kafolat",
            "description": (
                "Telegram Premium obunali haqiqiy akkauntlar\n"
                "kanalingizga obunachi bo'ladi.\n"
                "✅ 15 kun ichida tushsa — almashtiradi. Maks: 50 000 ta."
            ),
            "rate": 5.876, "min": 10, "max": 50_000,
        },
        {
            "service": 29994,
            "name": "💎 Premium a'zolar — 30 kun kafolat 🔥",
            "description": (
                "Telegram Premium obunali haqiqiy akkauntlar\n"
                "kanalingizga obunachi bo'ladi.\n"
                "🔥 30 kun ichida tushsa — almashtiradi.\n"
                "Eng mashhur premium variant. Maks: 50 000 ta."
            ),
            "rate": 10.1135, "min": 10, "max": 50_000,
        },
    ],
}
