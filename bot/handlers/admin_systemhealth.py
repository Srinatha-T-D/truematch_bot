# bot/handlers/admin_systemhealth.py

import time
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.database import fetch_one

BOT_START_TIME = time.time()


async def systemhealth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    # --- DB health ---
    try:
        db_ok = await fetch_one("SELECT 1")
        db_status = "✅ Connected"
    except Exception:
        db_status = "❌ DOWN"

    # --- Active chats ---
    active_chats = await fetch_one(
        """
        SELECT COUNT(*)
        FROM chat_sessions
        WHERE ended_at IS NULL
        """
    )

    # --- Recent messages (last 5 min) ---
    recent_msgs = await fetch_one(
        """
        SELECT COUNT(*)
        FROM chat_messages
        WHERE sent_at >= NOW() - INTERVAL '5 minutes'
        """
    )

    uptime_min = int((time.time() - BOT_START_TIME) / 60)

    message = (
        "🩺 *SYSTEM HEALTH*\n\n"
        f"🗄 Database: {db_status}\n"
        f"💬 Active Chats: {active_chats[0]}\n"
        f"📨 Msgs (5 min): {recent_msgs[0]}\n"
        f"⏱ Uptime: {uptime_min} min"
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        protect_content=True,
    )


systemhealth_handler = CommandHandler("systemhealth", systemhealth_command)
