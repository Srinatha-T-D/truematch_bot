# bot/handlers/help.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


HELP_TEXT = (
    "🤖 *TrueMatch Help*\n\n"
    "🟢 *Available Commands*\n\n"
    "/start – Start the bot or reset preferences\n"
    "/find – Find a new anonymous chat\n"
    "/next – Skip current chat and find a new one\n"
    "/stop – Exit current chat or matchmaking\n"
    "/vip – View VIP plans and upgrade\n"
    "/invite – Invite friends and earn VIP rewards\n"
    "/invites – View your invite stats and VIP rewards\n"
    "/rules – Read rules and privacy policy\n"
    "/help – Show this help message\n\n"
    "🔒 Your identity stays anonymous.\n"
    "🚫 Abuse or rule violations may result in a ban."
)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown",
        protect_content=True,
    )


# Exportable handler (consistent with other modules)
help_handler = CommandHandler("help", help_command)
