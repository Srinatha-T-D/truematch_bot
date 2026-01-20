# bot/handlers/admin_revenue.py

from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.database import fetch_one


async def revenue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    today_rev = await fetch_one(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE status = 'SUCCESS'
          AND DATE(created_at) = $1
        """,
        today,
    )

    month_rev = await fetch_one(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE status = 'SUCCESS'
          AND created_at >= $1
        """,
        month_start,
    )

    total_rev = await fetch_one(
        """
        SELECT COALESCE(SUM(amount), 0), COUNT(*)
        FROM payments
        WHERE status = 'SUCCESS'
        """
    )

    message = (
        "💰 *REVENUE STATS*\n\n"
        f"📅 Today: ₹{today_rev[0]}\n"
        f"📆 This Month: ₹{month_rev[0]}\n"
        f"🏦 Total: ₹{total_rev[0]}\n"
        f"🧾 Successful Payments: {total_rev[1]}"
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        protect_content=True,
    )


revenue_handler = CommandHandler("revenue", revenue_command)
