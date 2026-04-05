"""
core/constants.py — Zendor SMM Bot
Butun bot bo'ylab ishlatiladigan konstantlar.
"""

# Buyurtma holatlari (SMM API → O'zbekcha)
STATUS_UZ: dict[str, str] = {
    "Pending":     "⏳ Kutilmoqda",
    "In Progress": "🔄 Bajarilmoqda",
    "In progress": "🔄 Bajarilmoqda",
    "Processing":  "🔄 Jarayonda",
    "Completed":   "✅ Bajarildi",
    "Partial":     "⚠️ Qisman bajarildi",
    "Canceled":    "❌ Bekor qilindi",
    "Cancelled":   "❌ Bekor qilindi",
    "Refunded":    "💸 Qaytarildi",
}

STATUS_EMOJI: dict[str, str] = {
    "Pending":     "⏳",
    "In progress": "🔄",
    "In Progress": "🔄",
    "Processing":  "🔄",
    "Completed":   "✅",
    "Partial":     "⚠️",
    "Canceled":    "❌",
    "Cancelled":   "❌",
    "Refunded":    "💸",
}

# Yakunlangan holat — yangilanmaydi
FINAL_STATUSES: frozenset[str] = frozenset({
    "Completed", "Canceled", "Cancelled", "Refunded", "Partial"
})

# Referal turi — icon va label
REFERRAL_TYPE_META: dict[str, tuple[str, str]] = {
    "signup_bonus":  ("👤", "Ro'yxatdan o'tdi"),
    "deposit_bonus": ("💳", "Balans to'ldirdi"),
    "percent":       ("📦", "Buyurtma berdi"),
}

# Divider (qayta-qayta yozmaslik uchun)
DIVIDER = "━━━━━━━━━━━━━━━━━━━━━"
