# bot/handlers/admin_audit.py
# Admin live audit & moderation tools

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.matchmaking import ACTIVE_CHATS, disconnect_users
from bot.core.audit import log_admin_action

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# --------------------------------------------------
# /activechats
# --------------------------------------------------
async def active_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety
    if not update.message:
        return

    admin = update.effective_user
    if not _is_admin(admin.id):
        await update.message.reply_text("❌ Unauthorized")
        return

    if not ACTIVE_CHATS:
        await update.message.reply_text("🛡 No active chats right now.")
        return

    seen = set()
    lines = ["🛡 *Active Chats*\n"]

    i = 1
    for user_id, (partner_id, partner_chat_id, session_id) in ACTIVE_CHATS.items():
        if user_id in seen or partner_id in seen:
            continue

        seen.add(user_id)
        seen.add(partner_id)

        lines.append(
            f"{i}️⃣ `{user_id}` ↔ `{partner_id}`\n"
            f"Session: `{session_id}`"
        )
        i += 1

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        protect_content=True,
    )


# --------------------------------------------------
# /force_stop <user_id>
# --------------------------------------------------
async def force_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety
    if not update.message:
        return

    admin = update.effective_user
    if not _is_admin(admin.id):
        await update.message.reply_text("❌ Unauthorized")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/force_stop <user_id>",
            protect_content=True,
        )
        return

    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ user_id must be a number")
        return

    chat = ACTIVE_CHATS.get(target_user_id)
    if not chat:
        await update.message.reply_text("ℹ️ User is not in an active chat.")
        return

    partner_id, partner_chat_id, session_id = chat

    # Force disconnect (single source of truth)
    disconnect_users(target_user_id)

    # Notify both users (best-effort)
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text="⚠️ Chat ended by moderator.",
        )
        await context.bot.send_message(
            chat_id=partner_chat_id,
            text="⚠️ Chat ended by moderator.",
        )
    except Exception:
        pass

    # Audit log (best-effort)
    try:
        await log_admin_action(
            admin_id=admin.id,
            action="FORCE_STOP_CHAT",
            metadata={
                "session_id": session_id,
                "user_a": str(target_user_id),
                "user_b": str(partner_id),
            },
        )
    except Exception:
        pass

    logger.warning(
        "ADMIN FORCE STOP | admin=%s | users=%s,%s | session=%s",
        admin.id,
        target_user_id,
        partner_id,
        session_id,
    )

    await update.message.reply_text(
        "🛑 *Chat Force-Stopped*\n\n"
        f"User A: `{target_user_id}`\n"
        f"User B: `{partner_id}`\n"
        f"Session: `{session_id}`",
        parse_mode="Markdown",
        protect_content=True,
    )


# Export handlers
activechats_handler = CommandHandler("activechats", active_chats_command)
forcestop_handler = CommandHandler("force_stop", force_stop_command)
