# bot/handlers/error.py
# Global error handler (must NEVER crash)

import logging
from telegram.error import Conflict
from telegram.ext import ContextTypes

from bot.config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Global error handler for all unhandled exceptions.
    This function must NEVER raise.
    """

    err = context.error
    if not err:
        return

    # 🚫 Telegram Conflict is NOT an app error
    # Happens when multiple getUpdates / polling instances run
    if isinstance(err, Conflict):
        logger.warning(
            "Telegram Conflict detected (multiple getUpdates). Ignoring."
        )
        return

    # ✅ Log real errors with traceback
    logger.exception(
        "Unhandled exception while processing update",
        exc_info=err,
    )

    # 🔔 Notify admins (best-effort, never block)
    if not ADMIN_IDS:
        return

    try:
        error_text = (
            "🚨 *Bot Error Occurred*\n\n"
            f"`{type(err).__name__}: {err}`"
        )

        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=error_text,
                    parse_mode="Markdown",
                )
            except Exception:
                continue
    except Exception:
        # Absolute last safety net
        pass
