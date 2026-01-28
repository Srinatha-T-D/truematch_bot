# bot/handlers/verify.py
# User entry point for account verification

from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.logger import logger


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Reset any previous verification flow
    context.user_data.pop("verify", None)

    # Initialize verification session
    context.user_data["verify"] = {
        "step": "intro",
        "full_name": None,
        "gender": None,
        "contact": None,
    }

    logger.info("[VERIFY] User %s started verification", user_id)

    await update.message.reply_text(
        "🛡️ *Account Verification*\n\n"
        "Verification increases trust and helps reduce fake users.\n\n"
        "📌 You will be asked to provide details:\n"
        "• A quick anti-bot check\n\n"
        "👮 Admin approval is required.\n"
        "🔒 Your contact details are *never shared* with other users.\n\n"
        "👉 *Reply with your full name to continue.*",
        parse_mode="Markdown",
    )

    # Move to next step
    context.user_data["verify"]["step"] = "full_name"
