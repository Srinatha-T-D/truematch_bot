# bot/handlers/start.py

from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.core.database import fetch_one, execute
from bot.core.referral import apply_referral


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    # Check if user already exists
    row = await fetch_one(
        "SELECT user_id FROM users WHERE user_id = $1",
        user.id,
    )

    is_new_user = not row

    if is_new_user:
        # Create user
        await execute(
            """
            INSERT INTO users (user_id, trials_left, created_at)
            VALUES ($1, 5, $2)
            """,
            user.id,
            datetime.now(timezone.utc),
        )

        # ✅ HANDLE REFERRAL (FIRST START ONLY)
        if args:
            try:
                referrer_id = int(args[0])

                # 🚫 Prevent self-referral
                if referrer_id != user.id:
                    applied = await apply_referral(user.id, referrer_id)

                    if applied:
                        # Notify new user
                        await update.message.reply_text(
                            "🎉 You joined via an invite!\n"
                            "Your friend just earned VIP access!"
                        )

                        # 🔔 Notify referrer
                        try:
                            await context.bot.send_message(
                                chat_id=referrer_id,
                                text=(
                                    "🎉 *Invite Success!*\n\n"
                                    "Someone joined TrueMatch using your invite link.\n"
                                    "✨ Your VIP has been extended!"
                                ),
                                parse_mode="Markdown",
                            )
                        except Exception:
                            # Referrer might have blocked the bot
                            pass

                else:
                    await update.message.reply_text(
                        "⚠️ Self-invites are not allowed."
                    )

            except ValueError:
                pass

    # 🔘 MAIN MENU
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
        "👋 Welcome to *TrueMatch*!\n\n"
        "TrueMatch connects you with real people for anonymous 1-to-1 chats.\n\n"
        "🔐 Your identity is never shared\n"
        "🚫 No harassment, abuse, or spam\n"
        "🛡 Chats are moderated for safety\n\n"
        "👇 Choose an option below",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
