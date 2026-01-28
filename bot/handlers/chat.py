# bot/handlers/chat.py

from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import get_partner
from bot.core.chat_logger import log_message
from bot.core.timeout import mark_activity
from bot.core.db import get_db


def is_user_verified(user_id: int) -> bool:
    """
    Check if a user is verified.
    """
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT is_verified
                FROM users
                WHERE user_id = %s
                """,
                (str(user_id),),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    return bool(row and row.get("is_verified"))


async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-text messages
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text

    partner = get_partner(user.id)
    if not partner:
        return

    partner_id, partner_chat_id, session_id = partner

    # ⏱ Activity tracking (both sides)
    mark_activity(user.id)
    mark_activity(partner_id)

    # 🔐 Log message (sync, best-effort)
    try:
        log_message(session_id, user.id, text)
    except Exception:
        # Logging must never break chat flow
        pass

    # ✔️ Verified badge (sender-side)
    prefix = ""
    try:
        if is_user_verified(user.id):
            prefix = "✔️ Verified\n"
    except Exception:
        # Verification lookup must never break chat
        prefix = ""

    # 💬 Forward message to partner
    await context.bot.send_message(
        chat_id=partner_chat_id,
        text=f"{prefix}{text}",
    )
