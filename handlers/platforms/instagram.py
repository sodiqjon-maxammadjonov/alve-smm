"""
handlers/platforms/instagram.py — Zendor SMM Bot
Instagram platformasining barcha xizmatlari.

KAFOLAT TUSHUNTIRISH:
  ♻️ Kafolatli  = tushib ketsa bepul to'ldiriladi (refill)
  ⚡ Kafolatsiz = narxi arzon, lekin vaqt o'tishi bilan biroz kamayishi mumkin
                 Bu NORMAL holat — bot akkauntlar Instagram tomonidan aniqlanib
                 o'chirilib qolinishi natijasida sodir bo'ladi.
                 Pulni qaytarish yo'q, lekin juda katta tushish bo'lsa admin hal qiladi.
"""

INSTAGRAM_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 16286,
            "name": "⚡ Arzon — tez keladi",
            "description": (
                "Tez boshlanadi, soatiga 1–2 ming kishi keladi.\n"
                "💡 Narxi arzon bo'lgani uchun bot akkauntlar ishlatiladi.\n"
                "⚠️ Kafolatsiz: vaqt o'tishi bilan bir qismi tushib ketishi mumkin.\n"
                "   Bu normal — Instagram bot akkauntlarni o'chirib tashlaydi."
            ),
            "rate": 0.524, "min": 10, "max": 1_000_000,
        },
        {
            "service": 30106,
            "name": "✅ Real ko'rinishli + 60 kun kafolat",
            "description": (
                "Real odamga o'xshash akkauntlardan obunachilar keladi.\n"
                "✅ 60 kun ichida tushib ketsa — bepul to'ldirib beriladi.\n"
                "Kuniga 10–20 ming tezlik. Maksimal: 200 000 ta."
            ),
            "rate": 0.5198, "min": 10, "max": 200_000,
            "refill": True,
        },
        {
            "service": 30519,
            "name": "🔥 Premium — mobil app + 90 kun kafolat",
            "description": (
                "Mobil ilovali akkauntlardan keladi — eng sifatli variant.\n"
                "Past tushish darajasi, uzoq saqlanadi.\n"
                "🔥 90 kun ichida tushib ketsa — bepul to'ldirib beriladi.\n"
                "Maksimal: 5 000 000 ta."
            ),
            "rate": 0.5311, "min": 10, "max": 5_000_000,
            "refill": True,
        },
        {
            "service": 29254,
            "name": "🇺🇸 Amerika (AQSh) obunachilar",
            "description": (
                "AQSh akkauntlaridan obunachilar — xorijiy auditoriya uchun.\n"
                "✅ 60 kunlik sifat kafolati mavjud.\n"
                "Maksimal: 5 000 ta."
            ),
            "rate": 0.5085, "min": 10, "max": 5_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 16360,
            "name": "⚡ Arzon — darhol boshlanadi",
            "description": (
                "Darhol boshlanadi, juda tez yetkaziladi.\n"
                "💡 Arzon narx — bot akkauntlar ishlatiladi.\n"
                "⚠️ Kafolatsiz: bir qismi keyinchalik tushib ketishi mumkin.\n"
                "   Instagram bot layklar manbalarini bloklaydi ba'zan."
            ),
            "rate": 0.1017, "min": 10, "max": 250_000,
        },
        {
            "service": 29160,
            "name": "✅ Real ko'rinishli layklar",
            "description": (
                "Real odamlarga o'xshash akkauntlardan layklar.\n"
                "Past tushish darajasi, bardoshli natija.\n"
                "⚠️ Kafolatsiz, lekin sifat yaxshi. Maks: 200 000 ta."
            ),
            "rate": 0.1017, "min": 10, "max": 200_000,
        },
        {
            "service": 29566,
            "name": "♻️ Layklar + 30 kun kafolat",
            "description": (
                "Layklar qo'shiladi.\n"
                "✅ 30 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Maksimal: 1 000 000 ta."
            ),
            "rate": 0.1029, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29567,
            "name": "♻️ Layklar + 60 kun kafolat",
            "description": (
                "Layklar qo'shiladi.\n"
                "✅ 60 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Uzoqroq kafolat — narxi biroz yuqori. Maks: 1 000 000 ta."
            ),
            "rate": 0.1040, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💬 IZOHLAR (KAMENTARIYALAR)
    # ────────────────────────────────────────────────────────────
    "💬 Izohlar": [
        {
            "service": 29484,
            "name": "⚡ Tasodifiy izohlar — arzon",
            "description": (
                "Haqiqiy akkauntlardan tasodifiy ingliz/boshqa tildagi izohlar.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz: ba'zi akkauntlar o'chirilishi bilan izohlar yo'qolishi mumkin.\n"
                "Maksimal: 10 000 ta."
            ),
            "rate": 0.5085, "min": 10, "max": 10_000,
        },
        {
            "service": 29487,
            "name": "♻️ Tasodifiy izohlar + 30 kun kafolat",
            "description": (
                "Haqiqiy akkauntlardan tasodifiy izohlar.\n"
                "✅ 30 kun ichida yo'qolsa — bepul to'ldirib beriladi.\n"
                "Maksimal: 100 000 ta."
            ),
            "rate": 0.6215, "min": 10, "max": 100_000,
            "refill": True,
        },
        {
            "service": 29491,
            "name": "✍️ O'z matnli izoh — kafolatli",
            "description": (
                "Siz yozgan matn bilan izoh qoldiriladi.\n"
                "Har bir qatorga bitta izoh — buyurtma soniga teng.\n"
                "✅ 30 kun davomida kafolatlangan. Maks: 100 000 ta."
            ),
            "rate": 0.8475, "min": 10, "max": 100_000,
            "refill": True,
            "custom_comments": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👍 IZOHGA LAYK (Comment Likes)
    # ────────────────────────────────────────────────────────────
    "👍 Izohga layk": [
        {
            "service": 29260,
            "name": "⚡ Izohga layk — arzon",
            "description": (
                "Biror izoh (kamentariya) ostiga layk qo'shiladi.\n"
                "Izohingiz top'ga chiqishi uchun foydali.\n"
                "⚠️ Kafolatsiz variant. Maks: 10 000 ta."
            ),
            "rate": 0.17, "min": 10, "max": 10_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 28841,
            "name": "⚡ Ko'rishlar — arzon va tez",
            "description": (
                "Video va Reels ko'rishlar soni oshadi.\n"
                "Darhol boshlanadi, juda tez.\n"
                "⚠️ Kafolatsiz: arzon bo'lgani uchun bot ko'rishlar.\n"
                "   Instagram ba'zan bularni o'chirib tashlaydi."
            ),
            "rate": 0.0102, "min": 100, "max": 100_000,
        },
        {
            "service": 27250,
            "name": "♻️ Ko'rishlar + 30 kun kafolat",
            "description": (
                "Video va Reels ko'rishlar qo'shiladi.\n"
                "✅ 30 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Maksimal: 100 000 000 ta (100 million)."
            ),
            "rate": 0.0102, "min": 100, "max": 100_000_000,
            "refill": True,
        },
        {
            "service": 27268,
            "name": "♻️ Post ko'rishlar — kafolatli",
            "description": (
                "Oddiy postlar uchun ko'rishlar soni oshadi.\n"
                "✅ Kafolatlangan — tushib ketsa to'ldiriladi.\n"
                "Maksimal: 5 000 000 ta."
            ),
            "rate": 0.0113, "min": 100, "max": 5_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💾 SAQLASHLAR
    # ────────────────────────────────────────────────────────────
    "💾 Saqlashlar": [
        {
            "service": 18030,
            "name": "⚡ Saqlashlar — arzon",
            "description": (
                "Postingiz saqlashlar (bookmark) soni oshadi.\n"
                "Darhol boshlanadi, kuniga 50 000 tezlik.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0031, "min": 10, "max": 200_000,
        },
        {
            "service": 6291,
            "name": "✅ Saqlashlar — sifatli",
            "description": (
                "Sifatli akkauntlardan saqlashlar.\n"
                "Tez bajariladi, barqaror natija.\n"
                "⚠️ Kafolatsiz variant. Maks: 50 000 ta."
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
            "name": "⚡ Ulashishlar — arzon",
            "description": (
                "Postingiz ulashishlar (share) soni oshadi.\n"
                "Darhol boshlanadi, juda tez.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0091, "min": 10, "max": 2_100_000_000,
        },
        {
            "service": 26672,
            "name": "✅ Ulashishlar — sifatli",
            "description": (
                "Sifatli akkauntlardan ulashishlar.\n"
                "Tez bajariladi, barqaror natija.\n"
                "⚠️ Kafolatsiz variant. Maks: 10 000 000 ta."
            ),
            "rate": 0.0091, "min": 10, "max": 10_000_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 AKKAUNT BUYURTMA (Tayyor akkauntlar)
    # ────────────────────────────────────────────────────────────
    "🆕 Tayyor akkaunt": [
        {
            "service": 29800,
            "name": "📱 Yangi akkaunt — telefon orqali",
            "description": (
                "Telefon raqami orqali ro'yxatdan o'tkazilgan tayyor Instagram akkaunt.\n"
                "Email va parol beriladi.\n"
                "✅ Kafolatlangan — ishlamasa almashtiradi.\n"
                "💡 Yangi biznes yoki qo'shimcha akkaunt uchun."
            ),
            "rate": 1.50, "min": 1, "max": 10,
            "link_override": {
                "prompt": "📧 Akkaunt yuborilishi kerak bo'lgan email manzilingizni yozing:",
                "hint": "Email manzil",
                "example": "sizning@email.com",
                "validate": "email",
            },
        },
    ],
}
