"""
handlers/platforms/telegram.py — Zendor SMM Bot
Telegram platformasining barcha xizmatlari.

YANGI XIZMAT QO'SHISH:
  Tegishli bo'lim ro'yxatiga quyidagi formatda dict qo'shing:
  {
      "service": <Peakerr ID>,
      "name": "Nom",
      "description": "Tavsif",
      "rate": <USD/1000>,
      "min": <min>, "max": <max>,
      # Ixtiyoriy: "refill": True, "markup": 150.0, "link_override": {...}
  }
"""

TELEGRAM_SERVICES: dict[str, list[dict]] = {

    "👁 Ko'rishlar": [
        {
            "service": 15982,
            "name": "Ko'rishlar — Eng arzon ⚠️",
            "description": "⚡ Ultra tez, 1M/kun tezlik.\n⚠️ Kafolatsiz — tushib ketishi mumkin.",
            "rate": 0.0023, "min": 10, "max": 1_000_000,
        },
        {
            "service": 16926,
            "name": "Ko'rishlar — Barqaror ✅",
            "description": "Tushib ketmaydigan. 1 post.\n⚡ Darhol boshlanadi.",
            "rate": 0.0074, "min": 50, "max": 100_000_000,
        },
        {
            # Kanal linkini so'raydi (alohida link_override)
            "service": 15448,
            "name": "Ko'rishlar — So'nggi 5 post",
            "description": "Oxirgi 5 postga bir vaqtda.\n✅ Non-drop, barqaror.",
            "rate": 0.0429, "min": 50, "max": 50_000_000,
            "link_override": {
                "prompt": "📨 Kanal linkini yuboring:",
                "hint": "Kanal linki yoki username",
                "example": "https://t.me/kanalingiz  yoki  @kanalingiz",
                "validate": "telegram_channel",
            },
        },
        {
            "service": 28478,
            "name": "Premium ko'rishlar 💎",
            "description": "Faqat Telegram Premium akkauntlardan.\n✅ Eng sifatli va ishonchli.",
            "rate": 0.0911, "min": 10, "max": 150_000,
        },
    ],

    "😍 Reaksiyalar": [
        {
            "service": 18339,
            "name": "Aralash ijobiy reaksiyalar ⚠️",
            "description": "👍❤️🔥🎉🤩😁 — avtomatik aralash.\n⚠️ Kafolatsiz variant.",
            "rate": 0.0226, "min": 10, "max": 10_000_000,
        },
        {
            "service": 23335,
            "name": "👍 Like — Umrbod kafolat ♻️",
            "description": "Faqat 👍 reaksiya.\n✅ Umrbod saqlanadi.",
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23338,
            "name": "❤️ Yurak — Umrbod kafolat ♻️",
            "description": "Faqat ❤️ reaksiya.\n✅ Umrbod saqlanadi.",
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23339,
            "name": "🔥 Olov — Umrbod kafolat ♻️",
            "description": "Faqat 🔥 reaksiya.\n✅ Umrbod saqlanadi.",
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 23345,
            "name": "🎉 Bayram — Umrbod kafolat ♻️",
            "description": "Faqat 🎉 reaksiya.\n✅ Umrbod saqlanadi.",
            "rate": 0.0294, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    "👥 Obunachilar": [
        {
            "service": 29540,
            "name": "Obunachi — Arzon ⚠️",
            "description": "Real ko'rinishdagi akkauntlar. Tez.\n⚠️ Kafolatsiz.",
            "rate": 0.339, "min": 10, "max": 1_000_000,
        },
        {
            "service": 29541,
            "name": "Obunachi — 30 kun kafolat ♻️",
            "description": "Real akkauntlar.\n🛡 30 kun ichida tushsa bepul to'ldiriladi.",
            "rate": 0.3503, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29545,
            "name": "Obunachi — 365 kun kafolat ♻️",
            "description": "Real akkauntlar.\n🛡 1 yil davomida kafolatlangan.",
            "rate": 0.5311, "min": 10, "max": 1_000_000,
            "refill": True,
        },
        {
            "service": 29546,
            "name": "Obunachi — Umrbod kafolat ⭐",
            "description": "Real akkauntlar.\n🛡 Umrbod kafolat — eng ishonchli variant.",
            "rate": 0.5763, "min": 10, "max": 1_000_000,
            "refill": True,
        },
    ],

    "💎 Premium A'zolar": [
        {
            "service": 29989,
            "name": "Premium — 7 kun",
            "description": "💎 Telegram Premium akkauntlar.\n✅ 7 kun non-drop kafolati.",
            "rate": 3.3335, "min": 10, "max": 50_000,
        },
        {
            "service": 29991,
            "name": "Premium — 15 kun",
            "description": "💎 Telegram Premium akkauntlar.\n✅ 15 kun non-drop kafolati.",
            "rate": 5.876, "min": 10, "max": 50_000,
        },
        {
            "service": 29994,
            "name": "Premium — 30 kun ⭐",
            "description": "💎 Telegram Premium akkauntlar.\n🛡 30 kun non-drop — eng mashhur.",
            "rate": 10.1135, "min": 10, "max": 50_000,
        },
    ],
}
