# bot/handlers/error.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Global error handler for all unhandled exceptions.
    """

    logger.exception(
        "Unhandled exception while processing update:",
        exc_info=context.error,
    )

    # 🔔 Optional: notify admin(s)
    try:
        error_text = (
            "🚨 *Bot Error Occurred*\n\n"
            f"`{context.error}`"
        )

        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=error_text,
                parse_mode="Markdown",
            )
    except Exception:
        # Never allow error handler to crash
        pass
