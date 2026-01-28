# bot/handlers/vipstatus.py

from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.db import get_db


# ============================================================
# /vipstatus — USER VIP STATUS
# ============================================================

async def vipstatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    now = datetime.now(timezone.utc)

    user_id = str(user.id)  # ✅ DB column is TEXT

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT vip_until FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()

        if not row or not row["vip_until"] or row["vip_until"] <= now:
            await update.message.reply_text("❌ You do not have an active VIP.")
            return

        vip_until = row["vip_until"].strftime("%Y-%m-%d %H:%M UTC")

        await update.message.reply_text(
            f"⭐ *VIP Active*\n\n"
            f"Valid until: {vip_until}",
            parse_mode="Markdown",
        )

    finally:
        conn.close()
