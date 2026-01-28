# bot/config/settings.py
# SINGLE SOURCE OF TRUTH CONFIG
# Compatible with truematch_clean

import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# TELEGRAM
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

BOT_NAME = "AnonyLink"

# ============================================================
# DATABASE (ABSOLUTE AUTHORITY)
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# 🔒 HARD SAFETY: never touch anonylink accidentally
if "anonylink" in DATABASE_URL:
    raise RuntimeError(
        "❌ REFUSING TO START: DATABASE_URL points to anonylink"
    )

# ============================================================
# ENV
# ============================================================

BOT_ENV = os.getenv("BOT_ENV", "prod")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ============================================================
# REDIS
# ============================================================

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# ============================================================
# TRIAL SYSTEM
# ============================================================

FREE_TRIAL_COUNT = int(os.getenv("FREE_TRIAL_COUNT", "5"))

# ============================================================
# GLOBAL FREE WINDOW
# ============================================================

GLOBAL_FREE_START = date(1970, 1, 1)
GLOBAL_FREE_END = date(1970, 1, 1)

# ============================================================
# VIP (Telegram Stars)
# ============================================================

VIP_PRODUCT_ID = "anonylink_vip_30d"
VIP_PRICE_STARS = 50
VIP_DURATION_DAYS = 30

# ============================================================
# ADMIN
# ============================================================

ADMIN_IDS = {
    659916146,
    7132350913,  # your Telegram ID
}

# ============================================================
# REFERRALS
# ============================================================

REFERRAL_BONUS_DAYS = int(os.getenv("REFERRAL_BONUS_DAYS", "3"))
