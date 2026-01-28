# bot/handlers/admin_revenue.py

from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.db import get_db


async def revenue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

    if update.effective_user.id not in ADMIN_IDS:
        return

    today = datetime.now(timezone.utc).date()
    month_start = today.replace(day=1)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # -------------------------------
            # Today revenue
            # -------------------------------
            cur.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM payments
                WHERE status = 'SUCCESS'
                  AND DATE(created_at) = %s
                """,
                (today,),
            )
            today_rev = cur.fetchone()[0] or 0

            # -------------------------------
            # Month revenue
            # -------------------------------
            cur.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM payments
                WHERE status = 'SUCCESS'
                  AND created_at >= %s
                """,
                (month_start,),
            )
            month_rev = cur.fetchone()[0] or 0

            # -------------------------------
            # Total revenue + count
            # -------------------------------
            cur.execute(
                """
                SELECT COALESCE(SUM(amount), 0), COUNT(*)
                FROM payments
                WHERE status = 'SUCCESS'
                """
            )
            row = cur.fetchone()
            total_rev = row[0] or 0
            total_count = row[1] or 0

    finally:
        conn.close()

    message = (
        "💰 *REVENUE STATS*\n\n"
        f"📅 Today: ₹{today_rev}\n"
        f"📆 This Month: ₹{month_rev}\n"
        f"🏦 Total: ₹{total_rev}\n"
        f"🧾 Successful Payments: {total_count}"
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        protect_content=True,
    )


# Export handler
revenue_handler = CommandHandler("revenue", revenue_command)
