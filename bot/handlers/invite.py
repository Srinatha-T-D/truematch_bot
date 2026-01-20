from telegram import Update
from telegram.ext import ContextTypes

# 🔒 LOCKED TO VERIFIED WORKING USERNAME
BOT_USERNAME = "TrueMatch_Vip_bot"

async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    invite_link = f"https://t.me/{BOT_USERNAME}?start={user.id}"

    await update.message.reply_text(
        "🎁 Invite friends to TrueMatch!\n\n"
        "Share this link:\n"
        f"{invite_link}\n\n"
        "You’ll earn rewards when they join."
    )
