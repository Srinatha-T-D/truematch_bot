# bot/handlers/consent.py
# Handles Yes / No consent after no match

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import try_match, dequeue
from bot.utils.states import CONSENT_WAIT

logger = logging.getLogger(__name__)


async def consent_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    user = query.from_user
    chat_id = query.message.chat_id
    data = query.data

    # Only valid if we were actually waiting for consent
    if context.user_data.get("state") != CONSENT_WAIT:
        await query.edit_message_text("❗ This action is no longer valid.")
        return

    # Reset state immediately
    context.user_data.pop("state", None)

    # --------------------------
    # ❌ USER SAID NO
    # --------------------------
    if data == "consent_no":
        await dequeue(user.id)
        await query.edit_message_text(
            "❌ No problem. You’ve exited the queue."
        )
        logger.info("User %s declined relaxed matching", user.id)
        return

    # --------------------------
    # ✅ USER SAID YES
    # --------------------------
    if data == "consent_yes":
        await query.edit_message_text(
            "⏳ Connecting you to someone…"
        )

        matched = await try_match(
            user_id=user.id,
            chat_id=chat_id,
        )

        if matched:
            logger.info("User %s matched after consent", user.id)
            return

        await query.edit_message_text(
            "❌ Still no users available right now.\nPlease try again later."
        )
        logger.info("User %s consented but no match found", user.id)
        return

    # --------------------------
    # UNKNOWN CALLBACK
    # --------------------------
    await query.edit_message_text("❓ Unknown action.")
