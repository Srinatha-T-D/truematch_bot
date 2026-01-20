from telegram import Update
from telegram.ext import ContextTypes

RULES_TEXT = (
    "📜 *TrueMatch Rules & Privacy*\n\n"
    "✔ Be respectful — harassment is not tolerated\n"
    "✔ No spam, promotions, or scams\n"
    "✔ No sharing personal information\n"
    "✔ No illegal content\n\n"
    "🛡 Safety & Privacy:\n"
    "• Chats are anonymous\n"
    "• Messages may be temporarily stored for abuse prevention\n"
    "• Reported chats are reviewed by moderators\n"
    "• Chats auto-delete after 14 days\n\n"
    "Violations may lead to permanent bans."
)

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        RULES_TEXT,
        parse_mode="Markdown",
    )
