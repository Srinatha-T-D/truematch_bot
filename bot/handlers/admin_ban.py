# bot/handlers/admin_ban.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.db import get_db
from bot.core.audit import log_admin_action


# --------------------------------------------------
# /ban <user_id> [reason]
# --------------------------------------------------
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/ban <user_id> [reason]",
            protect_content=True,
        )
        return

    # user_id stored as TEXT
    try:
        user_id = str(int(context.args[0]))
    except ValueError:
        await update.message.reply_text("❌ Invalid user_id")
        return

    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Not specified"

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT is_banned FROM users WHERE user_id = %s",
                (user_id,),
            )
            user = cur.fetchone()

            if not user:
                await update.message.reply_text("❌ User not found.")
                return

            if user["is_banned"]:
                await update.message.reply_text("⚠️ User is already banned.")
                return

            cur.execute(
                "UPDATE users SET is_banned = TRUE WHERE user_id = %s",
                (user_id,),
            )

        conn.commit()
    finally:
        conn.close()

    # Audit log (best-effort)
    try:
        await log_admin_action(
            admin_id=admin_id,
            action="BAN_USER",
            metadata={"user_id": user_id, "reason": reason},
        )
    except Exception:
        pass

    await update.message.reply_text(
        "⛔ *User Banned*\n\n"
        f"User ID: `{user_id}`\n"
        f"Reason: {reason}",
        parse_mode="Markdown",
        protect_content=True,
    )


# --------------------------------------------------
# /unban <user_id>
# --------------------------------------------------
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety: ignore non-message updates
    if not update.message:
        return

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
        user_id = str(int(context.args[0]))
    except ValueError:
        await update.message.reply_text("❌ Invalid user_id")
        return

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT is_banned FROM users WHERE user_id = %s",
                (user_id,),
            )
            user = cur.fetchone()

            if not user:
                await update.message.reply_text("❌ User not found.")
                return

            if not user["is_banned"]:
                await update.message.reply_text("⚠️ User is not banned.")
                return

            cur.execute(
                "UPDATE users SET is_banned = FALSE WHERE user_id = %s",
                (user_id,),
            )

        conn.commit()
    finally:
        conn.close()

    # Audit log (best-effort)
    try:
        await log_admin_action(
            admin_id=admin_id,
            action="UNBAN_USER",
            metadata={"user_id": user_id},
        )
    except Exception:
        pass

    await update.message.reply_text(
        "✅ *User Unbanned*\n\n"
        f"User ID: `{user_id}`",
        parse_mode="Markdown",
        protect_content=True,
    )


# Export handlers
ban_handler = CommandHandler("ban", ban_command)
unban_handler = CommandHandler("unban", unban_command)
