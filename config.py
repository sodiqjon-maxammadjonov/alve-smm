"""
config.py — Zendor SMM Bot
Barcha sozlamalar .env dan yuklanadi.

Yangi sozlama qo'shish uchun:
  1. .env fayliga qiymat yozing
  2. Bu yerda os.getenv(...) bilan o'qing
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram Bot ───────────────────────────────────────────────
BOT_TOKEN      = os.getenv("BOT_TOKEN")
BOT_USERNAME   = os.getenv("BOT_USERNAME", "zendor_smm_bot")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "smo_2811")

# Admin ID larni vergul bilan ajratish mumkin: "111,222,333"
_admin_raw = os.getenv("ADMIN_ID", "7917217047")
try:
    ADMIN_IDS: list[int] = [int(x.strip()) for x in _admin_raw.split(",")]
except Exception:
    ADMIN_IDS = [int(_admin_raw)]

ADMIN_ID = ADMIN_IDS[0]                          # Asosiy admin
GROUP_ID = int(os.getenv("GROUP_ID", str(ADMIN_ID)))  # Depozit log guruhi

# ── SMM API (Peakerr) ──────────────────────────────────────────
SMM_API_URL = os.getenv("SMM_API_URL", "https://peakerr.com/api/v2")
SMM_API_KEY = os.getenv("SMM_API_KEY")

# ── Narx va valyuta ────────────────────────────────────────────
USD_TO_UZS      = float(os.getenv("USD_TO_UZS", "12000"))
MARKUP_PERCENT  = float(os.getenv("MARKUP_PERCENT", "200"))  # Global markup (%)

# ── To'lov ma'lumotlari ────────────────────────────────────────
CARD_NUMBER = os.getenv("CARD_NUMBER", "0000 0000 0000 0000")
CARD_OWNER  = os.getenv("CARD_OWNER", "Karta egasi")
MIN_DEPOSIT = int(os.getenv("MIN_DEPOSIT", "5000"))
MAX_DEPOSIT = int(os.getenv("MAX_DEPOSIT", "500000"))

# ── Referal dasturi ────────────────────────────────────────────
REFERRAL_PERCENT  = float(os.getenv("REFERRAL_PERCENT", "10"))   # Har buyurtmadan %
REFERRAL_BONUS    = int(os.getenv("REFERRAL_BONUS", "100"))       # Do'st ulashadigan bonus
SIGNUP_BONUS      = int(os.getenv("SIGNUP_BONUS", "100"))         # Yangi referal bonus
DEPOSIT_BONUS     = int(os.getenv("DEPOSIT_BONUS", "500"))        # Depozit qo'ysa bonus

# ── Auto-updater ───────────────────────────────────────────────
ORDER_UPDATE_INTERVAL = int(os.getenv("ORDER_UPDATE_INTERVAL", "300"))  # sekund (default 5 daq)
