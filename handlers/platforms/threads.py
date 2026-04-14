"""
handlers/platforms/threads.py — Zendor SMM Bot
Threads platformasining xizmatlari.
"""

THREADS_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 30765,
            "name": "⚡ Ko'rishlar",
            "description": (
                "Threads postlaringizga ko'rishlar qo'shiladi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 50 000 ta."
            ),
            "rate": 1.84, "min": 10, "max": 50_000,
        },
    ],

    "❤️ Layklar": [
        {
            "service": 30760,
            "name": "⚡ Layklar — arzon",
            "description": (
                "Bir necha daqiqada boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
        {
            "service": 29559,
            "name": "✅ Layklar — sifatli",
            "description": (
                "Haqiqiy ko'rinishdagi sifatli akkauntlardan layklar.\n"
                "Past tushish darajasi.\n"
                "⚠️ Kafolatsiz. Maks: 50 000 ta."
            ),
            "rate": 8.475, "min": 50, "max": 50_000,
        },
    ],

    "👤 Obunachilar": [
        {
            "service": 30759,
            "name": "⚡ Obunachilar — arzon",
            "description": (
                "Tez yetkaziladi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 5.53, "min": 10, "max": 5_000,
        },
        {
            "service": 29558,
            "name": "🔥 Obunachilar — sifatli + 30 kun kafolat",
            "description": (
                "Haqiqiy ko'rinishdagi sifatli akkauntlar.\n"
                "🔥 30 kun ichida tushsa — bepul to'ldirib beriladi.\n"
                "Maks: 50 000 ta."
            ),
            "rate": 16.95, "min": 100, "max": 50_000,
            "refill": True,
        },
    ],

    "🔄 Repostlar": [
        {
            "service": 30761,
            "name": "⚡ Repostlar — arzon",
            "description": (
                "Postingiz repost soni oshadi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 2.77, "min": 10, "max": 5_000,
        },
    ],

    "💾 Saqlashlar": [
        {
            "service": 30763,
            "name": "⚡ Saqlashlar",
            "description": (
                "Postingiz saqlashlar soni oshadi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    "💬 Izohlar": [
        {
            "service": 30764,
            "name": "⚡ Izohlar",
            "description": (
                "Postingizga izohlar qo'shiladi.\n"
                "Tez boshlanadi.\n"
                "⚠️ Kafolatsiz. Maks: 5 000 ta."
            ),
            "rate": 5.53, "min": 10, "max": 5_000,
        },
    ],
}
