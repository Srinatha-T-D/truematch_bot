# bot/handlers/invites.py

from datetime import timezone
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.users import get_or_create_user
from bot.core.db import get_db
from bot.core.referral import REFERRAL_BONUS_DAYS


async def invites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

    user = update.effective_user
    user_id = str(user.id)

    # Ensure user exists
    get_or_create_user(user.id)

    # --------------------------
    # DB read (report-style, no mutation)
    # --------------------------
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Count invited users
            cur.execute(
                "SELECT COUNT(*) FROM users WHERE referred_by = %s",
                (user_id,),
            )
            invite_count = cur.fetchone()[0] or 0

            vip_days_earned = invite_count * REFERRAL_BONUS_DAYS

            # Fetch VIP status
            cur.execute(
                "SELECT vip_until FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            vip_until = row["vip_until"] if row else None

    finally:
        conn.close()

    if vip_until:
        vip_until_str = vip_until.astimezone(timezone.utc).strftime("%d %b %Y")
    else:
        vip_until_str = "No active VIP"

    await update.message.reply_text(
        "🎁 *Your Invites*\n\n"
        f"👥 People invited: *{invite_count}*\n"
        f"⭐ VIP days earned: *{vip_days_earned} days*\n"
        f"⏰ VIP valid until: *{vip_until_str}*",
        parse_mode="Markdown",
    )
