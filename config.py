import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SMM_API_URL = os.getenv("SMM_API_URL", "https://peakerr.com/api/v2")
SMM_API_KEY = os.getenv("SMM_API_KEY")
USD_TO_UZS = float(os.getenv("USD_TO_UZS", "12000"))
MARKUP_PERCENT = float(os.getenv("MARKUP_PERCENT", "200"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GROUP_ID = int(os.getenv("GROUP_ID", os.getenv("ADMIN_ID")))
CARD_NUMBER = os.getenv("CARD_NUMBER")
CARD_OWNER = os.getenv("CARD_OWNER")
MIN_DEPOSIT = int(os.getenv("MIN_DEPOSIT", "5000"))
MAX_DEPOSIT = int(os.getenv("MAX_DEPOSIT", "500000"))
REFERRAL_PERCENT = float(os.getenv("REFERRAL_PERCENT", "10"))
REFERRAL_BONUS = int(os.getenv("REFERRAL_BONUS", "100"))
SIGNUP_BONUS = int(os.getenv("SIGNUP_BONUS", "100"))
DEPOSIT_BONUS = int(os.getenv("DEPOSIT_BONUS", "500"))

TELEGRAM_KEYWORDS = ["telegram", "tg", "телеграм"]
INSTAGRAM_KEYWORDS = ["instagram", "insta", "ig", "инстаграм"]

ALLOWED_CATEGORIES_TG = [
    "views", "members", "subscribers", "reactions", "premium",
    "post views", "channel", "group"
]

ALLOWED_CATEGORIES_IG = [
    "followers", "likes", "views", "story", "reel",
    "shares", "saves", "comments", "impressions"
]