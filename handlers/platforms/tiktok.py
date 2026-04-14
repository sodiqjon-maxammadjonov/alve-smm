"""
handlers/platforms/tiktok.py — Zendor SMM Bot
TikTok platformasining xizmatlari.
"""

TIKTOK_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 28676,
            "name": "⚡ Ko'rishlar — arzon va tez",
            "description": (
                "TikTok videolaringizga ko'rishlar qo'shiladi.\n"
                "Darhol boshlanadi, juda tez.\n"
                "💡 Arzon narx = bot ko'rishlar.\n"
                "⚠️ Kafolatsiz: biroz kamayishi mumkin vaqt o'tishi bilan."
            ),
            "rate": 0.0029, "min": 100, "max": 1_000_000,
        },
        {
            "service": 30086,
            "name": "✅ Ko'rishlar — sifatli, cheksiz",
            "description": (
                "Sifatli manbalardan ko'rishlar qo'shiladi.\n"
                "Cheksiz miqdorgacha buyurtma berish mumkin.\n"
                "⚠️ Kafolatsiz, lekin sifati yaxshi."
            ),
            "rate": 0.0032, "min": 100, "max": 100_000_000,
        },
        {
            "service": 30575,
            "name": "♻️ Ko'rishlar + 30 kun kafolat",
            "description": (
                "Sifatli akkauntlardan ko'rishlar qo'shiladi.\n"
                "✅ 30 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Cheksiz miqdorgacha."
            ),
            "rate": 0.0036, "min": 100, "max": 100_000_000,
            "refill": True,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 26332,
            "name": "⚡ Layklar — arzon",
            "description": (
                "0–5 daqiqada boshlanadi, juda tez.\n"
                "💡 Arzon narx bo'lgani uchun bot layklar.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0102, "min": 10, "max": 2_100_000_000,
        },
        {
            "service": 29584,
            "name": "♻️ Layklar + 30 kun kafolat",
            "description": (
                "Layklar qo'shiladi.\n"
                "✅ 30 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.0147, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29502,
            "name": "🔥 Sifatli layklar + 30 kun kafolat",
            "description": (
                "Sifatli akkauntlardan layklar qo'shiladi.\n"
                "🔥 30 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Maks: 50 000 ta."
            ),
            "rate": 0.0153, "min": 10, "max": 50_000,
            "refill": True,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 25001,
            "name": "⚡ Obunachilar — tez, arzon",
            "description": (
                "Haqiqiy ko'rinishdagi akkauntlar tez qo'shiladi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz: vaqt o'tishi bilan biroz kamayishi mumkin.\n"
                "   Bu TikTok bot akkauntlarni o'chirganda sodir bo'ladi."
            ),
            "rate": 0.1582, "min": 10, "max": 5_000_000,
        },
        {
            "service": 28175,
            "name": "♻️ Obunachilar + 10 kun kafolat",
            "description": (
                "Real ko'rinishdagi akkauntlar qo'shiladi.\n"
                "✅ 10 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 25002,
            "name": "💎 Profil rasmli + kafolatli",
            "description": (
                "Profil rasmi bor haqiqiy ko'rinishdagi akkauntlar.\n"
                "Eng ishonchli va sifatli variant.\n"
                "💎 Kafolatlangan — tushsa to'ldirib beriladi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    "💬 Izohlar": [
        {
            "service": 29270,
            "name": "⚡ Tasodifiy izohlar — arzon",
            "description": (
                "TikTok videolaringizga tasodifiy izohlar qo'shiladi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant. Maks: 2 000 ta."
            ),
            "rate": 0.85, "min": 5, "max": 2_000,
        },
    ],
}
