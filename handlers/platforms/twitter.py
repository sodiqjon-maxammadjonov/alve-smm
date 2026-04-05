"""
handlers/platforms/twitter.py — Zendor SMM Bot
Twitter / X platformasining xizmatlari.
"""

TWITTER_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 18322,
            "name": "Video ko'rishlar — Eng arzon ⚠️",
            "description": "⚡ Tez. Eng past narx.\n⚠️ Kafolat yo'q.",
            "rate": 0.0046, "min": 100, "max": 100_000_000,
        },
        {
            "service": 29859,
            "name": "Ko'rishlar + Impression ♻️",
            "description": "Ko'rishlar + impressionlar + engagement.\n♻️ Refill kafolatli.",
            "rate": 0.0047, "min": 100, "max": 2_147_483_647,
            "refill": True,
        },
        {
            "service": 15010,
            "name": "Tweet ko'rishlar — Tez ✅",
            "description": "⚡ 0–15 daqiqada boshlanadi.\nBarqaror sifat.",
            "rate": 0.0133, "min": 100, "max": 5_000_000,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 2634,
            "name": "Layklar — Tez ⚠️",
            "description": "⚡ Darhol boshlanadi. 3K/soat tezlik.\n⚠️ Kafolat yo'q.",
            "rate": 4.2086, "min": 10, "max": 100_000,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 15026,
            "name": "Obunachilar — Tez ⚠️",
            "description": "⚡ 0–15 daqiqada boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 1.3551, "min": 50, "max": 5_000,
        },
        {
            "service": 15030,
            "name": "Obunachilar — AQSh 🇺🇸",
            "description": "🇺🇸 AQSh akkauntlari. Sifatli.\n✅ Ishonchli variant.",
            "rate": 3.3296, "min": 100, "max": 10_000,
        },
    ],
}
