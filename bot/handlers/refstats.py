# bot/handlers/refstats.py

from telegram import Update
from telegram.ext import ContextTypes

from bot.core.db import get_db
from bot.core.referral import REFERRAL_BONUS_DAYS
from bot.utils.admin import is_admin


async def refstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

    user = update.effective_user

    # 🔒 Admin check
    if not is_admin(user.id):
        await update.message.reply_text(
            "⛔ You are not authorized to use this command."
        )
        return

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # -----------------------------
            # Total invited users
            # -----------------------------
            cur.execute(
                "SELECT COUNT(*) FROM users WHERE referred_by IS NOT NULL"
            )
            total_invites = cur.fetchone()[0] or 0

            total_vip_days = total_invites * REFERRAL_BONUS_DAYS

            # -----------------------------
            # Top inviters
            # -----------------------------
            cur.execute(
                """
                SELECT referred_by AS user_id, COUNT(*) AS cnt
                FROM users
                WHERE referred_by IS NOT NULL
                GROUP BY referred_by
                ORDER BY cnt DESC
                LIMIT 5
                """
            )
            top_rows = cur.fetchall() or []

    finally:
        conn.close()

    if top_rows:
        top_lines = []
        for idx, row in enumerate(top_rows, start=1):
            top_lines.append(
                f"{idx}️⃣ {row['user_id']} — {row['cnt']} invites"
            )
        top_text = "\n".join(top_lines)
    else:
        top_text = "No referrals yet."

    await update.message.reply_text(
        "📊 *Referral Stats (Admin)*\n\n"
        f"👥 Total invited users: *{total_invites}*\n"
        f"⭐ Total VIP days given: *{total_vip_days} days*\n\n"
        "🏆 *Top inviters:*\n"
        f"{top_text}",
        parse_mode="Markdown",
    )
