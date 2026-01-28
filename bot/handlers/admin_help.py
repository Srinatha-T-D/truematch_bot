# bot/handlers/admin_help.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS


ADMIN_HELP_TEXT = (
    "🛡️ *Truematch — Admin Commands*\n\n"

    "🔍 */readchat <session_uuid>*\n"
    "Export full anonymous chat as read-only CSV\n\n"

    "⛔ */force_stop*\n"
    "Force stop an active chat session\n\n"

    "💬 */activechats*\n"
    "View number of active chat sessions\n\n"

    "⭐ */grantvip <user_id> <days>*\n"
    "Manually grant VIP access to a user\n\n"

    "⛔ */ban <user_id> [reason]*\n"
    "Ban a user from using the bot\n\n"

    "✅ */unban <user_id>*\n"
    "Remove ban and restore user access\n\n"

    "📊 */stats*\n"
    "View overall bot statistics\n\n"

    "🩺 */systemhealth*\n"
    "Check database, chats, and bot health\n\n"

    "💰 */revenue*\n"
    "View real revenue from successful payments\n\n"

    "🚨 */alerts*\n"
    "View system, traffic, and payment alerts\n\n"

    "🗂️ */chat_history*\n"
    "View recent chat session history\n\n"

    "👁️ */view_chat*\n"
    "View chat metadata for moderation\n\n"

    "❓ */adminhelp*\n"
    "Show this admin command reference\n\n"

    "🔒 *Admin-only commands. All actions are audited.*"
)


async def adminhelp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

    if update.effective_user.id not in ADMIN_IDS:
        return

    await update.message.reply_text(
        ADMIN_HELP_TEXT,
        parse_mode="Markdown",
        protect_content=True,
    )


# Export handler (consistent with other admin modules)
adminhelp_handler = CommandHandler("adminhelp", adminhelp_command)
