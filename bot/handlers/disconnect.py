# bot/handlers/disconnect.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import get_partner, disconnect_users
from bot.utils.keyboards import report_keyboard

logger = logging.getLogger(__name__)


async def disconnect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /disconnect command handler
    """
    await _disconnect(update, context)


async def disconnect_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Disconnect button callback
    """
    query = update.callback_query
    await query.answer()
    await _disconnect(update, context)


async def _disconnect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    partner = get_partner(user.id)

    if not partner:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❗ You are not connected to anyone.",
        )
        return

    # ✅ FIX: unpack all 3 values (session_id is unused here)
    partner_user_id, partner_chat_id, session_id = partner

    # ✅ Correct call (single argument)
    disconnect_users(user.id)

    # Notify current user
    await context.bot.send_message(
        chat_id=chat_id,
        text="❌ Chat ended.",
    )

    # Show report option AFTER chat ends
    await context.bot.send_message(
        chat_id=chat_id,
        text="You can report this chat if needed.",
        reply_markup=report_keyboard(),
    )

    # Notify partner
    try:
        await context.bot.send_message(
            chat_id=partner_chat_id,
            text="❌ Chat ended.",
        )
    except Exception:
        pass

    logger.info(f"User {user.id} disconnected from {partner_user_id}")
