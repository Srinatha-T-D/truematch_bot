from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import get_partner
from bot.core.chat_logger import log_message
from bot.core.timeout import mark_activity


async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    partner = get_partner(user.id)
    if not partner:
        return

    partner_id, partner_chat_id, session_id = partner

    # activity tracking
    mark_activity(user.id)
    mark_activity(partner_id)

    # 🔐 log for admin safety
    await log_message(session_id, user.id, text)

    await context.bot.send_message(
        chat_id=partner_chat_id,
        text=text,
    )
