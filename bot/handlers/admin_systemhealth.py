# bot/handlers/admin_systemhealth.py
# Admin system health check (DB + sessions + uptime)

import time
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.db import get_db
from bot.core.redis import get_redis

BOT_START_TIME = time.time()


async def systemhealth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety
    if not update.message:
        return

    if update.effective_user.id not in ADMIN_IDS:
        return

    # -----------------------------
    # Database health
    # -----------------------------
    db_status = "❌ DOWN"
    active_chats = 0

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            db_status = "✅ Connected"

            # Active chat sessions
            cur.execute(
                """
                SELECT COUNT(*)
                FROM chat_sessions
                WHERE ended_at IS NULL
                """
            )
            active_chats = cur.fetchone()[0] or 0
    except Exception:
        db_status = "❌ DOWN"
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # -----------------------------
    # Redis health
    # -----------------------------
    redis_status = "❌ DOWN"
    try:
        redis = await get_redis()
        await redis.ping()
        redis_status = "✅ Connected"
    except Exception:
        redis_status = "❌ DOWN"

    # -----------------------------
    # Uptime
    # -----------------------------
    uptime_min = int((time.time() - BOT_START_TIME) / 60)

    message = (
        "🩺 *SYSTEM HEALTH*\n\n"
        f"🗄 Database: {db_status}\n"
        f"📦 Redis: {redis_status}\n"
        f"💬 Active Chats: {active_chats}\n"
        f"⏱ Uptime: {uptime_min} min"
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        protect_content=True,
    )


# Export handler
systemhealth_handler = CommandHandler("systemhealth", systemhealth_command)
