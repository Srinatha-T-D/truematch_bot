# bot/handlers/admin_alerts.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.database import fetch_one


# Thresholds (tune anytime)
MAX_ACTIVE_CHATS = 50
MAX_MSGS_5_MIN = 200
MAX_FAILED_PAYMENTS_1H = 3


async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    alerts = []

    # ── Active chats ─────────────────────────
    active_chats = await fetch_one(
        """
        SELECT COUNT(*)
        FROM chat_sessions
        WHERE ended_at IS NULL
        """
    )
    active_chats = active_chats[0]

    if active_chats > MAX_ACTIVE_CHATS:
        alerts.append(
            f"🔥 *High Active Chats*: {active_chats}"
        )

    # ── Message volume (5 min) ───────────────
    msgs_5min = await fetch_one(
        """
        SELECT COUNT(*)
        FROM chat_messages
        WHERE sent_at >= NOW() - INTERVAL '5 minutes'
        """
    )
    msgs_5min = msgs_5min[0]

    if msgs_5min > MAX_MSGS_5_MIN:
        alerts.append(
            f"📨 *High Message Volume (5m)*: {msgs_5min}"
        )

    # ── Failed payments (1 hour) ─────────────
    failed_payments = await fetch_one(
        """
        SELECT COUNT(*)
        FROM payments
        WHERE status = 'FAILED'
          AND created_at >= NOW() - INTERVAL '1 hour'
        """
    )
    failed_payments = failed_payments[0]

    if failed_payments > MAX_FAILED_PAYMENTS_1H:
        alerts.append(
            f"💸 *Payment Failures (1h)*: {failed_payments}"
        )

    # ── No activity check ────────────────────
    if active_chats == 0 and msgs_5min == 0:
        alerts.append(
            "⚠️ *No Activity Detected* (possible stall)"
        )

    # ── RESPONSE ─────────────────────────────
    if not alerts:
        message = (
            "🛎️ *System Alerts*\n\n"
            "✅ No alerts detected.\n"
            "System operating normally."
        )
    else:
        message = (
            "🚨 *System Alerts*\n\n"
            + "\n".join(alerts)
        )

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        protect_content=True,
    )


alerts_handler = CommandHandler("alerts", alerts_command)
