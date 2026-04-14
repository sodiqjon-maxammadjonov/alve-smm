"""
handlers/platforms/youtube.py — Zendor SMM Bot
YouTube platformasining xizmatlari.
"""

YOUTUBE_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 27356,
            "name": "⚡ Ko'rishlar — arzon va tez",
            "description": (
                "YouTube videolaringizga ko'rishlar qo'shiladi.\n"
                "Darhol boshlanadi.\n"
                "💡 Arzon narx = bot ko'rishlar ishlatiladi.\n"
                "⚠️ Kafolatsiz: YouTube bot ko'rishlarni aniqlab o'chirganda\n"
                "   soni biroz kamayishi mumkin. Bu platform xususiyati."
            ),
            "rate": 0.0364, "min": 100, "max": 1_000_000,
        },
        {
            "service": 27906,
            "name": "👑 Ko'rishlar — UMRBOD kafolat",
            "description": (
                "Tushib ketmaydigan yuqori sifatli ko'rishlar.\n"
                "👑 Umrbod kafolat — hech qachon tushib ketmaydi.\n"
                "Tezlik: kuniga 2 000 ta. VIP xizmat.\n"
                "Maks: 1 000 000 ta."
            ),
            "rate": 1.1639, "min": 100, "max": 1_000_000,
            "refill": True,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 24131,
            "name": "⚡ Layklar — arzon",
            "description": (
                "0–15 daqiqada boshlanadi.\n"
                "⚠️ Kafolatsiz variant. Maks: 20 000 ta."
            ),
            "rate": 0.1017, "min": 10, "max": 20_000,
        },
        {
            "service": 23991,
            "name": "♻️ Layklar + 6 oy kafolat",
            "description": (
                "Layklar qo'shiladi, kuniga 20 000 tezlik.\n"
                "✅ 6 oy davomida kafolatlangan — tushsa to'ldirib beriladi.\n"
                "Maks: 500 000 ta."
            ),
            "rate": 0.1582, "min": 10, "max": 500_000,
            "refill": True,
        },
        {
            "service": 24133,
            "name": "🔥 Sifatli layklar + 30 kun kafolat",
            "description": (
                "Profil rasmi bor sifatli akkauntlardan layklar.\n"
                "🔥 30 kun davomida kafolatlangan.\n"
                "Maks: 80 000 ta."
            ),
            "rate": 0.1695, "min": 10, "max": 80_000,
            "refill": True,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 30506,
            "name": "⚡ Obunachilar — arzon",
            "description": (
                "YouTube kanalingizga obunachilar qo'shiladi.\n"
                "Darhol boshlanadi.\n"
                "💡 Arzon narx = ba'zi bot akkauntlar.\n"
                "⚠️ Kafolatsiz: YouTube ba'zan bot akkauntlarni o'chiradi,\n"
                "   shu sababli obunachi soni biroz kamayishi mumkin.\n"
                "Maks: 30 000 ta."
            ),
            "rate": 0.0475, "min": 10, "max": 30_000,
        },
        {
            "service": 30507,
            "name": "✅ Obunachilar — katta hajm",
            "description": (
                "YouTube kanalingizga ko'p miqdorda obunachilar.\n"
                "Darhol boshlanadi, sifatli variant.\n"
                "⚠️ Kafolatsiz. Maks: 100 000 ta."
            ),
            "rate": 0.0645, "min": 10, "max": 100_000,
        },
    ],

    "💬 Izohlar": [
        {
            "service": 29100,
            "name": "⚡ Tasodifiy izohlar — arzon",
            "description": (
                "YouTube videolaringizga tasodifiy izohlar qo'shiladi.\n"
                "Haqiqiy ko'rinishdagi akkauntlardan.\n"
                "⚠️ Kafolatsiz variant. Maks: 5 000 ta."
            ),
            "rate": 1.13, "min": 5, "max": 5_000,
        },
    ],
}
