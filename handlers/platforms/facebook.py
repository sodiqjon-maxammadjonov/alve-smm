"""
handlers/platforms/facebook.py — Zendor SMM Bot
Facebook platformasining xizmatlari.
"""

FACEBOOK_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 28860,
            "name": "⚡ Ko'rishlar — arzon va tez",
            "description": (
                "0–5 daqiqada boshlanadi, kuniga 20–100 ming.\n"
                "💡 Arzon narx = bot ko'rishlar.\n"
                "⚠️ Kafolatsiz: Facebook bot ko'rishlarni aniqlaganda kamayishi mumkin."
            ),
            "rate": 0.0028, "min": 100, "max": 10_000_000,
        },
        {
            "service": 29449,
            "name": "✅ Video/Reels ko'rishlar — sifatli",
            "description": (
                "Video va Reels uchun sifatli ko'rishlar.\n"
                "Past tushish darajasi.\n"
                "⚠️ Kafolatsiz. Cheksiz miqdor."
            ),
            "rate": 0.0193, "min": 100, "max": 100_000_000,
        },
        {
            "service": 29450,
            "name": "♻️ Video/Reels ko'rishlar — kafolatli",
            "description": (
                "Video va Reels uchun sifatli ko'rishlar.\n"
                "✅ Kafolatlangan — tushsa bepul to'ldirib beriladi.\n"
                "Cheksiz miqdor."
            ),
            "rate": 0.0215, "min": 100, "max": 100_000_000,
            "refill": True,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 29577,
            "name": "⚡ Layklar — sifatli, arzon",
            "description": (
                "Sifatli akkauntlardan layklar qo'shiladi.\n"
                "Past tushish darajasi.\n"
                "⚠️ Kafolatsiz. Maks: 1 000 000 ta."
            ),
            "rate": 0.1300, "min": 10, "max": 1_000_000,
        },
        {
            "service": 29578,
            "name": "♻️ Layklar — sifatli + kafolatli",
            "description": (
                "Sifatli akkauntlardan layklar.\n"
                "✅ Kafolatlangan — tushsa bepul to'ldirib beriladi.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 0.1356, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 29443,
            "name": "⚡ Obunachilar — arzon",
            "description": (
                "Barcha turdagi sahifalarga obunachilar qo'shiladi.\n"
                "💡 Arzon narx = bot akkauntlar.\n"
                "⚠️ Kafolatsiz: vaqt o'tishi bilan biroz kamayishi mumkin."
            ),
            "rate": 0.1639, "min": 10, "max": 1_000_000,
        },
        {
            "service": 30130,
            "name": "✅ Obunachilar — sifatli",
            "description": (
                "Sifatli akkauntlardan obunachilar.\n"
                "Barcha turdagi Facebook sahifalari uchun.\n"
                "⚠️ Kafolatsiz, lekin sifati yaxshi. Maks: 1 000 000 ta."
            ),
            "rate": 0.1582, "min": 10, "max": 1_000_000,
        },
        {
            "service": 30131,
            "name": "🔥 Obunachilar — sifatli + kafolatli",
            "description": (
                "Sifatli akkauntlardan obunachilar.\n"
                "🔥 Kafolatlangan — tushsa bepul to'ldirib beriladi.\n"
                "Eng ishonchli variant. Maks: 1 000 000 ta."
            ),
            "rate": 0.1695, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],
}
