# bot/handlers/admin_audit.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import ADMIN_IDS
from bot.core.matchmaking import ACTIVE_CHATS, disconnect_users

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def active_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    for user_id, (partner_id, _) in ACTIVE_CHATS.items():
        if user_id in seen or partner_id in seen:
            continue

        seen.add(user_id)
        seen.add(partner_id)

        lines.append(f"{i}️⃣ `{user_id}` ↔ `{partner_id}`")
        i += 1

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )


async def force_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin = update.effective_user

    if not _is_admin(admin.id):
        await update.message.reply_text("❌ Unauthorized")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/force_stop <user_id>"
        )
        return

    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ user_id must be a number")
        return

    partner = ACTIVE_CHATS.get(target_user_id)

    if not partner:
        await update.message.reply_text("ℹ️ User is not in an active chat.")
        return

    partner_id, partner_chat_id = partner

    disconnect_users(target_user_id)

    # Notify both users (neutral message)
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

    logger.warning(
        f"ADMIN FORCE STOP | admin={admin.id} | users={target_user_id},{partner_id}"
    )

    await update.message.reply_text(
        f"🛑 Chat force-stopped between `{target_user_id}` and `{partner_id}`",
        parse_mode="Markdown",
    )
