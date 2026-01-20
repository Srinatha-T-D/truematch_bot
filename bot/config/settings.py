# bot/config/settings.py

from datetime import date
import os

# ============================================================
# TELEGRAM
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

# ============================================================
# BOT
# ============================================================

BOT_NAME = "AnonyLink"

# ============================================================
# GLOBAL FREE WINDOW
# ============================================================

# MUST be datetime.date objects
GLOBAL_FREE_START = date(2026, 1, 1)
GLOBAL_FREE_END = date(2026, 2, 25)

# ============================================================
# TRIALS
# ============================================================

FREE_TRIAL_COUNT = 5

# ============================================================
# VIP — TELEGRAM STARS
# ============================================================

VIP_PRODUCT_ID = "anonylink_vip_30d"
VIP_PRICE_STARS = 50
VIP_DURATION_DAYS = 30

# ============================================================
# REDIS
# ============================================================

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# ============================================================
# POSTGRESQL
# ============================================================

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "anonylink")
POSTGRES_USER = os.getenv("POSTGRES_USER", "anonylink")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

if not POSTGRES_PASSWORD:
    raise RuntimeError("POSTGRES_PASSWORD is not set in environment variables")

# ============================================================
# ADMIN
# ============================================================

# Telegram user IDs allowed to access admin commands
ADMIN_IDS = {
    659916146,   # <-- YOUR Telegram ID
}


REFERRAL_BONUS_DAYS = int(os.getenv("REFERRAL_BONUS_DAYS", "3"))
