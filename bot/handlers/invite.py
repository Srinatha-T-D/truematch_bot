# bot/handlers/invite.py

from telegram import Update
from telegram.ext import ContextTypes


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

    user = update.effective_user
    bot = context.bot

    # Get bot username dynamically (safe & future-proof)
    bot_username = bot.username
    invite_link = f"https://t.me/{bot_username}?start={user.id}"

    await update.message.reply_text(
        "🎁 *Invite friends to TrueMatch!*\n\n"
        "Share this link:\n"
        f"{invite_link}\n\n"
        "You’ll earn rewards when they join.",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
