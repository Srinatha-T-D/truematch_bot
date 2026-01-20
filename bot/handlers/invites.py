# bot/handlers/invites.py

from datetime import timezone
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.database import fetch_one
from bot.core.referral import REFERRAL_BONUS_DAYS


async def invites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Count how many users this person referred
    row = await fetch_one(
        "SELECT COUNT(*) AS cnt FROM users WHERE referred_by = $1",
        user.id,
    )

    invite_count = row["cnt"] if row else 0
    vip_days_earned = invite_count * REFERRAL_BONUS_DAYS

    # Fetch current VIP status
    vip_row = await fetch_one(
        "SELECT vip_until FROM users WHERE user_id = $1",
        user.id,
    )

    vip_until = vip_row["vip_until"] if vip_row else None

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
