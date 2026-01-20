# bot/handlers/message.py

from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import get_partner
from bot.core.timeout import mark_activity


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text

    partner = get_partner(user.id)
    if not partner:
        return

    partner_id, partner_chat_id = partner

    # ⏱ Mark activity for both users
    mark_activity(user.id)
    mark_activity(partner_id)

    await context.bot.send_message(
        chat_id=partner_chat_id,
        text=text,
    )
