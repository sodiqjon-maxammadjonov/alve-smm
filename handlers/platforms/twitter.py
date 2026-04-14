"""
handlers/platforms/twitter.py — Zendor SMM Bot
Twitter / X platformasining xizmatlari.
"""

TWITTER_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 18322,
            "name": "⚡ Ko'rishlar — arzon",
            "description": (
                "Tweet va video ko'rishlar qo'shiladi.\n"
                "Tez boshlanadi, eng past narx.\n"
                "⚠️ Kafolatsiz variant. Maks: 100 000 000 ta."
            ),
            "rate": 0.0046, "min": 100, "max": 100_000_000,
        },
        {
            "service": 29859,
            "name": "♻️ Ko'rishlar + ta'sir — kafolatli",
            "description": (
                "Ko'rishlar va faollik birga oshadi.\n"
                "✅ Kafolatlangan — tushsa bepul to'ldirib beriladi."
            ),
            "rate": 0.0047, "min": 100, "max": 2_147_483_647,
            "refill": True,
        },
        {
            "service": 15010,
            "name": "✅ Ko'rishlar — tez va barqaror",
            "description": (
                "0–15 daqiqada boshlanadi.\n"
                "Barqaror sifat, ishonchli variant. Maks: 5 000 000 ta."
            ),
            "rate": 0.0133, "min": 100, "max": 5_000_000,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 2634,
            "name": "⚡ Layklar — tez",
            "description": (
                "Darhol boshlanadi, soatiga 3 000 tezlik.\n"
                "⚠️ Kafolatsiz. Maks: 100 000 ta."
            ),
            "rate": 4.2086, "min": 10, "max": 100_000,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 15026,
            "name": "⚡ Obunachilar — arzon",
            "description": (
                "0–15 daqiqada boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 1.3551, "min": 50, "max": 5_000,
        },
        {
            "service": 15030,
            "name": "🇺🇸 Amerika obunachilar — sifatli",
            "description": (
                "AQSh akkauntlaridan sifatli obunachilar.\n"
                "✅ Ishonchli va sifatli variant. Maks: 10 000 ta."
            ),
            "rate": 3.3296, "min": 100, "max": 10_000,
        },
    ],
}
