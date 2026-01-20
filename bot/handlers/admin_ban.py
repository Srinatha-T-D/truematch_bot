# bot/handlers/admin_ban.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.database import fetch_one, execute
from bot.core.audit import log_admin_action


# --------------------------------------------------
# /ban <user_id> [reason]
# --------------------------------------------------
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/ban <user_id> [reason]",
            protect_content=True,
        )
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Not specified"

    user = await fetch_one(
        "SELECT is_banned FROM users WHERE user_id = $1",
        user_id,
    )

    if not user:
        await update.message.reply_text("❌ User not found.")
        return

    if user["is_banned"]:
        await update.message.reply_text("⚠️ User is already banned.")
        return

    await execute(
        "UPDATE users SET is_banned = TRUE WHERE user_id = $1",
        user_id,
    )

    await log_admin_action(
        admin_id=admin_id,
        action="BAN_USER",
        metadata={"user_id": user_id, "reason": reason},
    )

    await update.message.reply_text(
        f"⛔ *User Banned*\n\n"
        f"User ID: `{user_id}`\n"
        f"Reason: {reason}",
        parse_mode="Markdown",
        protect_content=True,
    )


# --------------------------------------------------
# /unban <user_id>
# --------------------------------------------------
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/unban <user_id>",
            protect_content=True,
        )
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    user = await fetch_one(
        "SELECT is_banned FROM users WHERE user_id = $1",
        user_id,
    )

    if not user:
        await update.message.reply_text("❌ User not found.")
        return

    if not user["is_banned"]:
        await update.message.reply_text("⚠️ User is not banned.")
        return

    await execute(
        "UPDATE users SET is_banned = FALSE WHERE user_id = $1",
        user_id,
    )

    await log_admin_action(
        admin_id=admin_id,
        action="UNBAN_USER",
        metadata={"user_id": user_id},
    )

    await update.message.reply_text(
        f"✅ *User Unbanned*\n\nUser ID: `{user_id}`",
        parse_mode="Markdown",
        protect_content=True,
    )


ban_handler = CommandHandler("ban", ban_command)
unban_handler = CommandHandler("unban", unban_command)
