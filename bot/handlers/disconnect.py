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

    partner_user_id, partner_chat_id = partner

    # ✅ Correct call (single argument)
    disconnect_users(user.id)

    await context.bot.send_message(
        chat_id=chat_id,
        text="❌ You have disconnected.",
    )
    # after notifying user about disconnect
    await context.bot.send_message(
       chat_id=chat_id,
       text="Chat ended.",
       reply_markup=report_keyboard(),
    )
    try:
        await context.bot.send_message(
            chat_id=partner_chat_id,
            text="❌ Your partner has disconnected.",
        )
    except Exception:
        pass

    logger.info(f"User {user.id} disconnected from {partner_user_id}")
