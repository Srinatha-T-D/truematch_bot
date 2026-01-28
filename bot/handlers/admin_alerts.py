# bot/handlers/admin_alerts.py
# Admin system alerts (safe & architecture-aligned)

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.db import get_db


# Thresholds (tune anytime)
MAX_ACTIVE_CHATS = 50
MAX_FAILED_PAYMENTS_1H = 3


async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety
    if not update.message:
        return

    if update.effective_user.id not in ADMIN_IDS:
        return

    alerts = []

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # ── Active chats ─────────────────────────
            cur.execute(
                """
                SELECT COUNT(*)
                FROM chat_sessions
                WHERE ended_at IS NULL
                """
            )
            active_chats = cur.fetchone()[0] or 0

            if active_chats > MAX_ACTIVE_CHATS:
                alerts.append(
                    f"🔥 *High Active Chats*: {active_chats}"
                )

            # ── Failed payments (last 1 hour) ─────────
            cur.execute(
                """
                SELECT COUNT(*)
                FROM payments
                WHERE status = 'FAILED'
                  AND created_at >= NOW() - INTERVAL '1 hour'
                """
            )
            failed_payments = cur.fetchone()[0] or 0

            if failed_payments > MAX_FAILED_PAYMENTS_1H:
                alerts.append(
                    f"💸 *Payment Failures (1h)*: {failed_payments}"
                )

    finally:
        conn.close()

    # ── No activity alert ─────────────────────
    if active_chats == 0:
        alerts.append(
            "⚠️ *No Active Chats* (possible stall)"
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


# Export handler
alerts_handler = CommandHandler("alerts", alerts_command)
