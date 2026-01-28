from telegram import Update
from telegram.ext import ContextTypes

from bot.services.admin_features.email_collection import EmailCollectionService


async def collect_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    success = await EmailCollectionService.save_email(user_id, text)

    if not success:
        await update.message.reply_text(
            "❌ Invalid email format.\nPlease send a valid email address."
        )
        return

    await update.message.reply_text(
        "✅ Email saved successfully!\n\n"
        "You’ll receive updates about offers, free days, and new features.\n"
        "You can opt out anytime using /unsubscribe."
    )

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await EmailCollectionService.opt_out(user_id)

    await update.message.reply_text(
        "🚫 You’ve unsubscribed from email updates.\n"
        "You will no longer receive announcements."
    )
