# bot/handlers/profile.py

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from bot.handlers.match import enqueue_for_match

logger = logging.getLogger(__name__)


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    # ==========================
    # GENDER SELECTION
    # ==========================
    if data.startswith("gender:"):
        gender = data.split(":", 1)[1]
        context.user_data["gender"] = gender

        logger.info(f"User {user.id} selected gender: {gender}")

        keyboard = [
            [
                InlineKeyboardButton("♂️ Male", callback_data="looking:male"),
                InlineKeyboardButton("♀️ Female", callback_data="looking:female"),
            ],
            [
                InlineKeyboardButton("🌈 Any", callback_data="looking:any"),
            ],
        ]

        try:
            await query.edit_message_text(
                text="🔍 *Who are you looking for?*",
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
        context.user_data["looking_for"] = looking_for

        logger.info(
            f"User {user.id} profile complete | "
            f"gender={context.user_data.get('gender')} | "
            f"looking_for={looking_for}"
        )

        try:
            await query.edit_message_text(
                text=(
                    "✅ *You’re all set!*\n\n"
                    "🔍 Use /find to start chatting\n"
                    "🎁 Use /invite to invite friends & earn rewards\n"
                    "📜 Use /rules to read guidelines"
                ),
                parse_mode="Markdown",
            )
        except BadRequest:
            pass

        # 🚀 NOW MATCH
