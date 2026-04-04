# handlers/services/link_examples.py
# Har bir platforma va bo'lim uchun link misoli va yo'riqnoma
# Yangi xizmat qo'shganda shu faylga ham qo'shing

LINK_EXAMPLES = {
    # ── TELEGRAM ──────────────────────────────────────────────
    "✈️ Telegram": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Telegram post linki",
            "example": "https://t.me/kanalingiz/123",
            "validate": "telegram_post",
        },
        "😍 Reaksiyalar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Telegram post linki",
            "example": "https://t.me/kanalingiz/123",
            "validate": "telegram_post",
        },
        "👥 Obunachilar": {
            "prompt": "📨 Kanal yoki guruh linkini yuboring:",
            "hint": "Kanal yoki guruh linki / username",
            "example": "https://t.me/kanalingiz  yoki  @kanalingiz",
            "validate": "telegram_channel",
        },
    },

    # ── INSTAGRAM ──────────────────────────────────────────────
    "📸 Instagram": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Post yoki Reel linkini yuboring:",
            "hint": "Instagram post/reel linki",
            "example": "https://www.instagram.com/p/ABC123xyz/",
            "validate": "url",
        },
        "❤️ Layklar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Instagram post linki",
            "example": "https://www.instagram.com/p/ABC123xyz/",
            "validate": "url",
        },
        "👤 Obunachilar": {
            "prompt": "📨 Profil linkini yuboring:",
            "hint": "Instagram profil linki yoki username",
            "example": "https://www.instagram.com/username/  yoki  @username",
            "validate": "url_or_username",
        },
        "🔄 Ulashishlar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Instagram post linki",
            "example": "https://www.instagram.com/p/ABC123xyz/",
            "validate": "url",
        },
    },

    # ── TIKTOK ──────────────────────────────────────────────
    "🎵 TikTok": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "TikTok video linki",
            "example": "https://www.tiktok.com/@username/video/1234567890",
            "validate": "url",
        },
        "❤️ Layklar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "TikTok video linki",
            "example": "https://www.tiktok.com/@username/video/1234567890",
            "validate": "url",
        },
        "👤 Obunachilar": {
            "prompt": "📨 Profil linkini yuboring:",
            "hint": "TikTok profil linki yoki username",
            "example": "https://www.tiktok.com/@username  yoki  @username",
            "validate": "url_or_username",
        },
        "🔄 Ulashishlar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "TikTok video linki",
            "example": "https://www.tiktok.com/@username/video/1234567890",
            "validate": "url",
        },
        "💬 Izohlar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "TikTok video linki",
            "example": "https://www.tiktok.com/@username/video/1234567890",
            "validate": "url",
        },
        "💾 Saqlashlar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "TikTok video linki",
            "example": "https://www.tiktok.com/@username/video/1234567890",
            "validate": "url",
        },
    },

    # ── YOUTUBE ──────────────────────────────────────────────
    "▶️ YouTube": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "YouTube video linki",
            "example": "https://www.youtube.com/watch?v=XXXXXXXXXXX\n  yoki  https://youtu.be/XXXXXXXXXXX",
            "validate": "url",
        },
        "👍 Layklar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "YouTube video linki",
            "example": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
            "validate": "url",
        },
        "🔔 Obunachi.": {
            "prompt": "📨 Kanal linkini yuboring:",
            "hint": "YouTube kanal linki",
            "example": "https://www.youtube.com/@kanalingiz\n  yoki  https://www.youtube.com/channel/UCxxxxxxx",
            "validate": "url",
        },
        "💬 Izohlar": {
            "prompt": "📨 Video linkini yuboring:",
            "hint": "YouTube video linki",
            "example": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
            "validate": "url",
        },
    },

    # ── FACEBOOK ──────────────────────────────────────────────
    "📘 Facebook": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Video yoki Reel linkini yuboring:",
            "hint": "Facebook video linki",
            "example": "https://www.facebook.com/watch?v=1234567890\n  yoki  https://fb.watch/xxxxxxx",
            "validate": "url",
        },
        "👍 Layklar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Facebook post linki",
            "example": "https://www.facebook.com/sahifangiz/posts/1234567890",
            "validate": "url",
        },
        "👥 Obunachilar": {
            "prompt": "📨 Sahifa yoki profil linkini yuboring:",
            "hint": "Facebook sahifa linki",
            "example": "https://www.facebook.com/sahifangiz",
            "validate": "url",
        },
    },

    # ── THREADS ──────────────────────────────────────────────
    "🧵 Threads": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Threads post linki",
            "example": "https://www.threads.net/@username/post/ABC123",
            "validate": "url",
        },
        "❤️ Layklar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Threads post linki",
            "example": "https://www.threads.net/@username/post/ABC123",
            "validate": "url",
        },
        "👤 Obunachilar": {
            "prompt": "📨 Profil linkini yuboring:",
            "hint": "Threads profil linki yoki username",
            "example": "https://www.threads.net/@username  yoki  @username",
            "validate": "url_or_username",
        },
        "🔄 Repostlar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Threads post linki",
            "example": "https://www.threads.net/@username/post/ABC123",
            "validate": "url",
        },
        "💬 Izohlar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Threads post linki",
            "example": "https://www.threads.net/@username/post/ABC123",
            "validate": "url",
        },
        "💾 Saqlashlar": {
            "prompt": "📨 Post linkini yuboring:",
            "hint": "Threads post linki",
            "example": "https://www.threads.net/@username/post/ABC123",
            "validate": "url",
        },
    },

    # ── TWITTER / X ──────────────────────────────────────────
    "🐦 Twitter / X": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Tweet linkini yuboring:",
            "hint": "Twitter/X tweet linki",
            "example": "https://x.com/username/status/1234567890123456789",
            "validate": "url",
        },
        "❤️ Layklar": {
            "prompt": "📨 Tweet linkini yuboring:",
            "hint": "Twitter/X tweet linki",
            "example": "https://x.com/username/status/1234567890123456789",
            "validate": "url",
        },
        "👤 Obunachilar": {
            "prompt": "📨 Profil linkini yuboring:",
            "hint": "Twitter/X profil linki yoki username",
            "example": "https://x.com/username  yoki  @username",
            "validate": "url_or_username",
        },
    },

    # ── PINTEREST ──────────────────────────────────────────────
    "📌 Pinterest": {
        "👁 Ko'rishlar": {
            "prompt": "📨 Pin linkini yuboring:",
            "hint": "Pinterest pin linki",
            "example": "https://www.pinterest.com/pin/1234567890/",
            "validate": "url",
        },
        "❤️ Layklar": {
            "prompt": "📨 Pin linkini yuboring:",
            "hint": "Pinterest pin linki",
            "example": "https://www.pinterest.com/pin/1234567890/",
            "validate": "url",
        },
        "👤 Obunachilar": {
            "prompt": "📨 Profil linkini yuboring:",
            "hint": "Pinterest profil linki",
            "example": "https://www.pinterest.com/username/",
            "validate": "url",
        },
        "🔄 Ulashishlar": {
            "prompt": "📨 Pin linkini yuboring:",
            "hint": "Pinterest pin linki",
            "example": "https://www.pinterest.com/pin/1234567890/",
            "validate": "url",
        },
        "💾 Saqlashlar": {
            "prompt": "📨 Pin linkini yuboring:",
            "hint": "Pinterest pin linki",
            "example": "https://www.pinterest.com/pin/1234567890/",
            "validate": "url",
        },
        "💬 Izohlar": {
            "prompt": "📨 Pin linkini yuboring:",
            "hint": "Pinterest pin linki",
            "example": "https://www.pinterest.com/pin/1234567890/",
            "validate": "url",
        },
    },

    # ════════════════════════════════════════════════════════
    # KELAJAK — O'YINLAR (yangi xizmat qo'shganda misol):
    # ════════════════════════════════════════════════════════
    # "🎮 O'yinlar": {
    #     "💎 Donatlar": {
    #         "prompt": "📨 O'yin ID yoki username yuboring:",
    #         "hint": "O'yin akkaunt ID yoki username",
    #         "example": (
    #             "PUBG uchun: 5123456789 (Player ID)\n"
    #             "MLBB uchun: 123456789 (User ID) + 1234 (Zone ID)\n"
    #             "  → Formatda yuboring: 123456789#1234\n"
    #             "Free Fire uchun: 1234567890 (UID)"
    #         ),
    #         "validate": "game_id",
    #     },
    # },
}


def get_link_info(platform: str, section: str) -> dict:
    """Platforma va bo'lim uchun link ma'lumotini qaytaradi"""
    default = {
        "prompt": "📨 Link yuboring:",
        "hint": "To'g'ri link",
        "example": "https://...",
        "validate": "url",
    }
    return LINK_EXAMPLES.get(platform, {}).get(section, default)


def validate_link(link: str, validate_type: str) -> bool:
    """Link to'g'riligini tekshiradi"""
    link = link.strip()

    if validate_type == "telegram_post":
        return (
            link.startswith("https://t.me/") and
            "/" in link[13:] and
            link[13:].split("/")[-1].isdigit()
        )
    elif validate_type == "telegram_channel":
        return (
            link.startswith("https://t.me/") or
            link.startswith("@") or
            link.startswith("t.me/")
        )
    elif validate_type == "url_or_username":
        return link.startswith("http") or link.startswith("@")
    elif validate_type == "url":
        return link.startswith("http")
    elif validate_type == "game_id":
        # O'yin ID larini tekshirish: raqam yoki raqam#raqam
        import re
        return bool(re.match(r'^\d+(\#\d+)?$', link))

    return link.startswith("http") or link.startswith("@")