"""
handlers/platforms/youtube.py — Zendor SMM Bot
YouTube platformasining xizmatlari.
"""

YOUTUBE_SERVICES: dict[str, list[dict]] = {

    # ────────────────────────────────────────────────────────────
    # 👁 KO'RISHLAR
    # ────────────────────────────────────────────────────────────
    "👁 Ko'rishlar": [
        {
            "service": 27356,
            "name": "Ko'rishlar — Arzon ⚡",
            "description": (
                "YouTube videolaringizga ko'rishlar.\n"
                "Tez boshlanadi.\n"
                "⚠️ Kafolatsiz variant."
            ),
            "rate": 0.0364, "min": 100, "max": 1_000_000,
        },
        {
            "service": 27906,
            "name": "Ko'rishlar — Umrbod kafolat 👑",
            "description": (
                "Tushib ketmaydigan sifatli ko'rishlar.\n"
                "👑 Umrbod kafolat — hech qachon tushib ketmaydi.\n"
                "Tezlik: kuniga 2 ming ta. VIP xizmat."
            ),
            "rate": 1.1639, "min": 100, "max": 1_000_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # ❤️ LAYKLAR
    # ────────────────────────────────────────────────────────────
    "❤️ Layklar": [
        {
            "service": 24131,
            "name": "Layklar — Arzon ⚡",
            "description": (
                "0-15 daqiqada boshlanadi.\n"
                "⚠️ Kafolatsiz variant. Max: 20 ming ta."
            ),
            "rate": 0.1017, "min": 10, "max": 20_000,
        },
        {
            "service": 20363,
            "name": "Layklar — Maxsus server ✅",
            "description": (
                "Xususiy server orqali tez yetkaziladi.\n"
                "⚠️ Kafolatsiz variant. Max: 50 ming ta."
            ),
            "rate": 0.1017, "min": 10, "max": 50_000,
        },
        {
            "service": 23991,
            "name": "Layklar — 6 oylik kafolat ♻️",
            "description": (
                "Layklar qo'shiladi, kuniga 20 ming tezlik.\n"
                "✅ 6 oy davomida kafolatlangan. Max: 500 ming ta."
            ),
            "rate": 0.1582, "min": 10, "max": 500_000,
            "refill": True,
        },
        {
            "service": 24133,
            "name": "Layklar — Sifatli + 30 kun kafolat 🔥",
            "description": (
                "Profil rasmi bor sifatli akkauntlardan layklar.\n"
                "🔥 30 kun davomida kafolatlangan. Max: 80 ming ta."
            ),
            "rate": 0.1695, "min": 10, "max": 80_000,
            "refill": True,
        },
    ],

    # ────────────────────────────────────────────────────────────
    # 👤 OBUNACHILAR
    # ────────────────────────────────────────────────────────────
    "👤 Obunachilar": [
        {
            "service": 30506,
            "name": "Obunachilar — Arzon ⚡",
            "description": (
                "Kanalingizga obunachilar qo'shiladi.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant. Max: 30 ming ta."
            ),
            "rate": 0.0475, "min": 10, "max": 30_000,
        },
        {
            "service": 30507,
            "name": "Obunachilar — Katta hajm ✅",
            "description": (
                "Kanalingizga ko'p miqdorda obunachilar.\n"
                "Darhol boshlanadi.\n"
                "⚠️ Kafolatsiz variant. Max: 100 ming ta."
            ),
            "rate": 0.0645, "min": 10, "max": 100_000,
        },
    ],
}