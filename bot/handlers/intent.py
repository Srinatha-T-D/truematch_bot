# bot/handlers/intent.py

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from bot.handlers.payments import send_vip_invoice

logger = logging.getLogger(__name__)


async def intent_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    # ⭐ VIP BUY — ALWAYS ALLOWED
    if data == "vip:buy":
        await send_vip_invoice(update, context)
        return

    if not data.startswith("intent:"):
        return

    intent = data.split(":", 1)[1]
    context.user_data.clear()
    context.user_data["intent"] = intent

    logger.info(f"User {user.id} selected intent: {intent}")

    # 🔹 NEXT STEP: GENDER SELECTION
    keyboard = [
        [
            InlineKeyboardButton("♂️ Male", callback_data="gender:male"),
            InlineKeyboardButton("♀️ Female", callback_data="gender:female"),
        ]
    ]

    try:
        await query.edit_message_text(
            text="👤 *Select your gender:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    except BadRequest:
        pass
