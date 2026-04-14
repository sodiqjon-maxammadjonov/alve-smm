"""
handlers/link_config.py — Zendor SMM Bot
Har platforma/bo'lim uchun link namunalari va validatsiya.

YANGI BO'LIM QO'SHISH:
  LINK_CONFIG dict ga tegishli kalit bilan qo'shing:
  "Platforma|||Bo'lim": { "prompt": ..., "example": ..., "validate": ... }
"""

# ── Validatsiya turlari ────────────────────────────────────────
# "url"            — http/https bilan boshlanishi kerak
# "url_or_username"— http yoki @ bilan
# "telegram_post"  — https://t.me/kanal/123 formatda
# "telegram_channel"— https://t.me/kanal yoki @kanal
# "username_only"  — faqat @ bilan boshlanuvchi
# "game_id"        — raqam yoki raqam#raqam (MLBB uchun)

LINK_CONFIG: dict[str, dict] = {

    # ── Telegram ──────────────────────────────────────────────
    "✈️ Telegram|||👁 Ko'rishlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Telegram post linki",
        "example":  "https://t.me/kanalingiz/123",
        "validate": "telegram_post",
    },
    "✈️ Telegram|||😍 Reaksiyalar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Telegram post linki",
        "example":  "https://t.me/kanalingiz/123",
        "validate": "telegram_post",
    },
    "✈️ Telegram|||👥 Obunachilar": {
        "prompt":   "📨 Kanal yoki guruh linkini yuboring:",
        "hint":     "Kanal linki yoki username",
        "example":  "https://t.me/kanalingiz  yoki  @kanalingiz",
        "validate": "telegram_channel",
    },
    "✈️ Telegram|||💎 Premium A'zolar": {
        "prompt":   "📨 Kanal yoki guruh linkini yuboring:",
        "hint":     "Kanal linki yoki username",
        "example":  "https://t.me/kanalingiz  yoki  @kanalingiz",
        "validate": "telegram_channel",
    },

    # ── Instagram ─────────────────────────────────────────────
    "📸 Instagram|||👁 Ko'rishlar": {
        "prompt":   "📨 Post yoki Reel linkini yuboring:",
        "hint":     "Instagram post/reel linki",
        "example":  "https://www.instagram.com/p/ABC123xyz/",
        "validate": "url",
    },
    "📸 Instagram|||❤️ Layklar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Instagram post linki",
        "example":  "https://www.instagram.com/p/ABC123xyz/",
        "validate": "url",
    },
    "📸 Instagram|||👤 Obunachilar": {
        "prompt":   "📨 Profil linkini yuboring:",
        "hint":     "Instagram profil linki yoki username",
        "example":  "https://www.instagram.com/username/  yoki  @username",
        "validate": "url_or_username",
    },
    "📸 Instagram|||🔄 Repostlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Instagram post linki",
        "example":  "https://www.instagram.com/p/ABC123xyz/",
        "validate": "url",
    },
    "📸 Instagram|||💬 Izohlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Instagram post linki",
        "example":  "https://www.instagram.com/p/ABC123xyz/",
        "validate": "url",
    },
    "📸 Instagram|||💾 Saqlashlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Instagram post linki",
        "example":  "https://www.instagram.com/p/ABC123xyz/",
        "validate": "url",
    },

    # ── TikTok ────────────────────────────────────────────────
    "🎵 TikTok|||👁 Ko'rishlar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "TikTok video linki",
        "example":  "https://www.tiktok.com/@username/video/1234567890",
        "validate": "url",
    },
    "🎵 TikTok|||❤️ Layklar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "TikTok video linki",
        "example":  "https://www.tiktok.com/@username/video/1234567890",
        "validate": "url",
    },
    "🎵 TikTok|||👤 Obunachilar": {
        "prompt":   "📨 Profil linkini yuboring:",
        "hint":     "TikTok profil linki yoki username",
        "example":  "https://www.tiktok.com/@username  yoki  @username",
        "validate": "url_or_username",
    },
    "🎵 TikTok|||🔄 Ulashishlar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "TikTok video linki",
        "example":  "https://www.tiktok.com/@username/video/1234567890",
        "validate": "url",
    },
    "🎵 TikTok|||💬 Izohlar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "TikTok video linki",
        "example":  "https://www.tiktok.com/@username/video/1234567890",
        "validate": "url",
    },
    "🎵 TikTok|||💾 Saqlashlar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "TikTok video linki",
        "example":  "https://www.tiktok.com/@username/video/1234567890",
        "validate": "url",
    },

    # ── YouTube ───────────────────────────────────────────────
    "▶️ YouTube|||👁 Ko'rishlar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "YouTube video linki",
        "example":  "https://www.youtube.com/watch?v=XXXXXXXXXXX\n  yoki  https://youtu.be/XXXXXXXXXXX",
        "validate": "url",
    },
    "▶️ YouTube|||👍 Layklar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "YouTube video linki",
        "example":  "https://www.youtube.com/watch?v=XXXXXXXXXXX",
        "validate": "url",
    },
    "▶️ YouTube|||🔔 Obunachi.": {
        "prompt":   "📨 Kanal linkini yuboring:",
        "hint":     "YouTube kanal linki",
        "example":  "https://www.youtube.com/@kanalingiz",
        "validate": "url",
    },
    "▶️ YouTube|||💬 Izohlar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "YouTube video linki",
        "example":  "https://www.youtube.com/watch?v=XXXXXXXXXXX",
        "validate": "url",
    },

    # ── Facebook ──────────────────────────────────────────────
    "📘 Facebook|||👁 Ko'rishlar": {
        "prompt":   "📨 Video linkini yuboring:",
        "hint":     "Facebook video linki",
        "example":  "https://www.facebook.com/watch?v=1234567890",
        "validate": "url",
    },
    "📘 Facebook|||👍 Layklar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Facebook post linki",
        "example":  "https://www.facebook.com/sahifangiz/posts/1234567890",
        "validate": "url",
    },
    "📘 Facebook|||👥 Obunachilar": {
        "prompt":   "📨 Sahifa linkini yuboring:",
        "hint":     "Facebook sahifa linki",
        "example":  "https://www.facebook.com/sahifangiz",
        "validate": "url",
    },

    # ── Twitter / X ───────────────────────────────────────────
    "🐦 Twitter / X|||👁 Ko'rishlar": {
        "prompt":   "📨 Tweet linkini yuboring:",
        "hint":     "Twitter/X tweet linki",
        "example":  "https://x.com/username/status/1234567890123456789",
        "validate": "url",
    },
    "🐦 Twitter / X|||❤️ Layklar": {
        "prompt":   "📨 Tweet linkini yuboring:",
        "hint":     "Twitter/X tweet linki",
        "example":  "https://x.com/username/status/1234567890123456789",
        "validate": "url",
    },
    "🐦 Twitter / X|||👤 Obunachilar": {
        "prompt":   "📨 Profil linkini yuboring:",
        "hint":     "Twitter/X profil linki yoki username",
        "example":  "https://x.com/username  yoki  @username",
        "validate": "url_or_username",
    },

    # ── Threads ───────────────────────────────────────────────
    "🧵 Threads|||👁 Ko'rishlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Threads post linki",
        "example":  "https://www.threads.net/@username/post/ABC123",
        "validate": "url",
    },
    "🧵 Threads|||❤️ Layklar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Threads post linki",
        "example":  "https://www.threads.net/@username/post/ABC123",
        "validate": "url",
    },
    "🧵 Threads|||👤 Obunachilar": {
        "prompt":   "📨 Profil linkini yuboring:",
        "hint":     "Threads profil linki yoki username",
        "example":  "https://www.threads.net/@username  yoki  @username",
        "validate": "url_or_username",
    },
    "🧵 Threads|||🔄 Repostlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Threads post linki",
        "example":  "https://www.threads.net/@username/post/ABC123",
        "validate": "url",
    },
    "🧵 Threads|||💬 Izohlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Threads post linki",
        "example":  "https://www.threads.net/@username/post/ABC123",
        "validate": "url",
    },
    "🧵 Threads|||💾 Saqlashlar": {
        "prompt":   "📨 Post linkini yuboring:",
        "hint":     "Threads post linki",
        "example":  "https://www.threads.net/@username/post/ABC123",
        "validate": "url",
    },

    # ── Pinterest ─────────────────────────────────────────────
    "📌 Pinterest|||👁 Ko'rishlar": {
        "prompt":   "📨 Pin linkini yuboring:",
        "hint":     "Pinterest pin linki",
        "example":  "https://www.pinterest.com/pin/1234567890/",
        "validate": "url",
    },
    "📌 Pinterest|||❤️ Layklar": {
        "prompt":   "📨 Pin linkini yuboring:",
        "hint":     "Pinterest pin linki",
        "example":  "https://www.pinterest.com/pin/1234567890/",
        "validate": "url",
    },
    "📌 Pinterest|||👤 Obunachilar": {
        "prompt":   "📨 Profil linkini yuboring:",
        "hint":     "Pinterest profil linki",
        "example":  "https://www.pinterest.com/username/",
        "validate": "url",
    },
    "📌 Pinterest|||🔄 Ulashishlar": {
        "prompt":   "📨 Pin linkini yuboring:",
        "hint":     "Pinterest pin linki",
        "example":  "https://www.pinterest.com/pin/1234567890/",
        "validate": "url",
    },
    "📌 Pinterest|||💾 Saqlashlar": {
        "prompt":   "📨 Pin linkini yuboring:",
        "hint":     "Pinterest pin linki",
        "example":  "https://www.pinterest.com/pin/1234567890/",
        "validate": "url",
    },
    "📌 Pinterest|||💬 Izohlar": {
        "prompt":   "📨 Pin linkini yuboring:",
        "hint":     "Pinterest pin linki",
        "example":  "https://www.pinterest.com/pin/1234567890/",
        "validate": "url",
    },
}

_DEFAULT_LINK_INFO = {
    "prompt":   "📨 Link yuboring:",
    "hint":     "To'g'ri link",
    "example":  "https://...",
    "validate": "url",
}


def get_link_info(platform: str, section: str) -> dict:
    """Platforma + bo'lim uchun link konfiguratsiyasini qaytaradi."""
    key = f"{platform}|||{section}"
    return LINK_CONFIG.get(key, _DEFAULT_LINK_INFO)


def validate_link(link: str, validate_type: str) -> bool:
    """
    Link formatini tekshiradi.
    Yangi validatsiya turi kerak bo'lsa — bu yerga qo'shing.
    """
    link = link.strip()
    if not link:
        return False

    if validate_type == "telegram_post":
        # https://t.me/kanal/123
        if not link.startswith("https://t.me/"):
            return False
        parts = link[13:].split("/")
        return len(parts) >= 2 and parts[-1].isdigit()

    if validate_type == "telegram_channel":
        return (
            link.startswith("https://t.me/")
            or link.startswith("@")
            or link.startswith("t.me/")
        )

    if validate_type == "url_or_username":
        return link.startswith("http") or link.startswith("@")

    if validate_type == "username_only":
        return link.startswith("@") and len(link) > 1

    if validate_type == "game_id":
        import re
        return bool(re.match(r"^\d+(\#\d+)?$", link))

    if validate_type == "email":
        import re
        return bool(re.match(r"^[\w.+\-]+@[\w\-]+\.[\w.\-]+$", link))

    # default: "url"
    return link.startswith("http://") or link.startswith("https://")

# ── Qo'shimcha Instagram bo'limlari ───────────────────────────────────────
LINK_CONFIG["📸 Instagram|||🔄 Ulashishlar"] = {
    "prompt": "📨 Post linkini yuboring:",
    "hint": "Instagram post linki",
    "example": "https://www.instagram.com/p/ABC123xyz/",
    "validate": "url",
}
LINK_CONFIG["📸 Instagram|||👍 Izohga layk"] = {
    "prompt": "📨 Izoh linkini yuboring (post link ham bo'ladi):",
    "hint": "Instagram post linki",
    "example": "https://www.instagram.com/p/ABC123xyz/",
    "validate": "url",
}
LINK_CONFIG["📸 Instagram|||🆕 Tayyor akkaunt"] = {
    "prompt": "📧 Akkaunt yuborilishi kerak bo'lgan email manzilingizni yozing:",
    "hint": "Email manzil",
    "example": "sizning@email.com",
    "validate": "email",
}

# YouTube bo'limlari nomlarini to'g'rilash
LINK_CONFIG["▶️ YouTube|||❤️ Layklar"] = LINK_CONFIG.get("▶️ YouTube|||👍 Layklar", {
    "prompt": "📨 Video linkini yuboring:",
    "hint": "YouTube video linki",
    "example": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
    "validate": "url",
})
LINK_CONFIG["▶️ YouTube|||👤 Obunachilar"] = LINK_CONFIG.get("▶️ YouTube|||🔔 Obunachi.", {
    "prompt": "📨 Kanal linkini yuboring:",
    "hint": "YouTube kanal linki",
    "example": "https://www.youtube.com/@kanalingiz",
    "validate": "url",
})
LINK_CONFIG["▶️ YouTube|||💬 Izohlar"] = {
    "prompt": "📨 Video linkini yuboring:",
    "hint": "YouTube video linki",
    "example": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
    "validate": "url",
}

# Telegram premium a'zolar nomini to'g'rilash
LINK_CONFIG["✈️ Telegram|||💎 Premium a'zolar"] = {
    "prompt": "📨 Kanal yoki guruh linkini yuboring:",
    "hint": "Kanal linki yoki username",
    "example": "https://t.me/kanalingiz  yoki  @kanalingiz",
    "validate": "telegram_channel",
}
