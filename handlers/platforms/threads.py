"""
handlers/platforms/threads.py — Zendor SMM Bot
Threads platformasining xizmatlari.

Eslatma: Threads xizmatlari boshqa platformalarga nisbatan qimmatroq —
bu provayderning o'z narxi.
"""

THREADS_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 30765,
            "name": "Ko'rishlar ⚡",
            "description": (
                "Threads postlaringizga ko'rishlar.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 1.84, "min": 10, "max": 50_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 30760,
            "name": "Layklar — Arzon ⚡",
            "description": (
                "Bir necha daqiqada boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
        {
            "service": 29559,
            "name": "Layklar — Sifatli ✅",
            "description": (
                "Haqiqiy ko'rinishdagi sifatli akkauntlardan layklar.\n"
                "Past tushish darajasi.\n"
                "⚠️ Kafolatsiz variant. Max: 50 ming ta."
            ),
            "rate": 8.475, "min": 50, "max": 50_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 30759,
            "name": "Obunachilar — Arzon ⚡",
            "description": (
                "Tez yetkaziladi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 5.53, "min": 10, "max": 5_000,
        },
        {
            "service": 29557,
            "name": "Obunachilar — Sifatli ✅",
            "description": (
                "Haqiqiy ko'rinishdagi sifatli akkauntlar.\n"
                "⚠️ Kafolatsiz variant. Max: 50 ming ta."
            ),
            "rate": 15.255, "min": 100, "max": 50_000,
        },
        {
            "service": 29558,
            "name": "Obunachilar — Sifatli + 30 kun kafolat 🔥",
            "description": (
                "Haqiqiy ko'rinishdagi sifatli akkauntlar.\n"
                "🔥 30 kun ichida tushib ketsa, bepul to'ldiriladi.\n"
                "Max: 50 ming ta."
            ),
            "rate": 16.95, "min": 100, "max": 50_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 🔄 REPOSTLAR
    # ────────────────────────────────────────────────────────────
    "🔄 Repostlar": [
        {
            "service": 30761,
            "name": "Repostlar — Arzon ⚡",
            "description": (
                "Postingiz repost soni oshadi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 2.77, "min": 10, "max": 5_000,
        },
        {
            "service": 29561,
            "name": "Repostlar — Sifatli ✅",
            "description": (
                "Sifatli akkauntlardan repostlar.\n"
                "Past tushish darajasi.\n"
                "⚠️ Kafolatsiz variant. Max: 50 ming ta."
            ),
            "rate": 20.34, "min": 50, "max": 50_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💾 SAQLASHLAR
    # ────────────────────────────────────────────────────────────
    "💾 Saqlashlar": [
        {
            "service": 30763,
            "name": "Saqlashlar ⚡",
            "description": (
                "Postingiz saqlashlar soni oshadi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 1.84, "min": 10, "max": 5_000,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 💬 IZOHLAR
    # ────────────────────────────────────────────────────────────
    "💬 Izohlar": [
        {
            "service": 30764,
            "name": "Izohlar ⚡",
            "description": (
                "Postingizga izohlar qo'shiladi.\n"
                "Tez boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 5.53, "min": 10, "max": 5_000,
        },
    ],
}