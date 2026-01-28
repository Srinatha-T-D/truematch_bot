# bot/handlers/profile.py
# Profile registration callbacks (FINAL, CLEAN)

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from bot.core.users import update_user_preferences
from bot.handlers.match import match_command

logger = logging.getLogger(__name__)


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    user = query.from_user
    user_id = str(user.id)
    data = query.data

    # ==========================
    # GENDER SELECTION
    # ==========================
    if data.startswith("gender:"):
        gender = data.split(":", 1)[1]

        update_user_preferences(user_id, gender=gender)

        logger.info("User %s selected gender: %s", user_id, gender)

        keyboard = [
            [
                InlineKeyboardButton("👨 Men", callback_data="looking:male"),
                InlineKeyboardButton("👩 Women", callback_data="looking:female"),
            ],
        ]

        try:
            await query.edit_message_text(
                text="🔍 *Who are you looking to chat with?*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )
        except BadRequest:
            pass

        return

    # ==========================
    # LOOKING FOR SELECTION
    # ==========================
    if data.startswith("looking:"):
        looking_for = data.split(":", 1)[1]

        update_user_preferences(user_id, looking_for=looking_for)

        logger.info(
            "User %s profile complete | gender + looking_for saved",
            user_id,
        )

        try:
            await query.edit_message_text(
                text=(
                    "✅ *You’re all set!*\n\n"
                    "🔍 Finding a match for you now…"
                ),
                parse_mode="Markdown",
            )
        except BadRequest:
            pass

        # 🚀 Resume matching using the ONLY supported entry point
        await match_command(update, context)
        return
