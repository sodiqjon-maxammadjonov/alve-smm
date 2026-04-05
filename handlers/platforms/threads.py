"""
handlers/platforms/threads.py — Zendor SMM Bot
Threads platformasining xizmatlari.
"""

THREADS_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 31001,
            "name": "Ko'rishlar ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 1.84, "min": 10, "max": 50_000,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 31002,
            "name": "Layklar ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 31003,
            "name": "Obunachilar ⚠️",
            "description": "⚠️ Kafolat yo'q.",
            "rate": 5.52, "min": 10, "max": 5_000,
        },
    ],

    "🔄 Repostlar": [
        {
            "service": 31004,
            "name": "Repostlar ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 2.00, "min": 10, "max": 5_000,
        },
    ],

    "💬 Izohlar": [
        {
            "service": 31005,
            "name": "Izohlar",
            "description": "Post izohlarini oshiradi.",
            "rate": 5.53, "min": 10, "max": 5_000,
        },
    ],

    "💾 Saqlashlar": [
        {
            "service": 31006,
            "name": "Saqlashlar ⚠️",
            "description": "⚡ Darhol boshlanadi.\n⚠️ Kafolat yo'q.",
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],
}
