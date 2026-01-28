# bot/handlers/reset_profile.py
# Admin / test command to force profile re-registration

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.db import get_db

logger = logging.getLogger(__name__)


async def reset_profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    # OPTIONAL: restrict to admin only
    # If you already have admin check util, use it here
    # Example:
    # if not is_admin(user_id):
    #     await update.message.reply_text("❌ You are not allowed to use this command.")
    #     return

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET gender = NULL,
                    looking_for = NULL
                WHERE user_id = %s
                """,
                (user_id,),
            )
            conn.commit()
    finally:
        conn.close()

    logger.warning("Profile reset for user %s", user_id)

    await update.message.reply_text(
        "🔄 *Profile reset successful!*\n\n"
        "Please type /start to register again.",
        parse_mode="Markdown",
    )
