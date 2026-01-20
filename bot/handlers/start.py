# bot/handlers/start.py

from datetime import datetime, timezone
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from bot.core.database import fetch_one, execute
from bot.core.referral import apply_referral


# ============================================================
# /start — ENTRY POINT + INTENT SELECTION
# ============================================================

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    # Check if user exists
    row = await fetch_one(
        "SELECT user_id FROM users WHERE user_id = $1",
        user.id,
    )

    is_new_user = not row

    if is_new_user:
        await execute(
            """
            INSERT INTO users (user_id, trials_left, created_at)
            VALUES ($1, 5, $2)
            """,
            user.id,
            datetime.now(timezone.utc),
        )

        # Apply referral ONLY on first start
        if args:
            try:
                referrer_id = int(args[0])
                await apply_referral(user.id, referrer_id)
            except ValueError:
                pass

    # 🔘 INTENT SELECTION (matches existing intent_callback)
    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Find Anonymous Chat",
                callback_data="intent:chat",
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ Buy VIP",
                callback_data="vip:buy",
            )
        ],
    ]

    await update.message.reply_text(
        "👋 *Welcome to TrueMatch*\n\n"
        "Choose what you want to do:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )
