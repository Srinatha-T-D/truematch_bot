# bot/handlers/stop.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import get_partner, disconnect_users
from bot.core.redis import get_redis

logger = logging.getLogger(__name__)


# =========================
# QUEUE CLEANUP
# =========================

async def _remove_from_all_queues(user_id: int):
    """
    Remove user from all Redis matchmaking queues (best-effort).
    """
    redis = await get_redis()
    keys = await redis.keys("queue:*")

    for key in keys:
        items = await redis.lrange(key, 0, -1)
        for item in items:
            try:
                q_user_id, _ = item.split(":")
                if int(q_user_id) == int(user_id):
                    await redis.lrem(key, 1, item)
            except Exception:
                continue


# =========================
# /stop COMMAND
# =========================

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id

    partner = get_partner(user_id)

    # --------------------------
    # 🔴 END ACTIVE CHAT
    # --------------------------
    if partner:
        partner_id, partner_chat_id, _ = partner

        # End chat session (safe if already ended)
        disconnect_users(user_id)

        # Notify current user
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "❌ Chat ended.\n\n"
                "🔁 What would you like to do next?\n\n"
                "/find   – Find a new chat\n"
                "/stop   – Exit matchmaking\n"
                "/invite – Invite friends & earn rewards"
            ),
        )

        # Notify partner (best-effort)
        try:
            await context.bot.send_message(
                chat_id=partner_chat_id,
                text="❌ Chat ended.",
            )
        except Exception:
            pass

        # Cleanup queues for both users
        await _remove_from_all_queues(user_id)
        await _remove_from_all_queues(partner_id)

        logger.info(
            "Chat stopped | user=%s partner=%s",
            user_id,
            partner_id,
        )

        return

    # --------------------------
    # 🧹 NOT IN CHAT → CLEAN EXIT
    # --------------------------
    await _remove_from_all_queues(user_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🛑 You have exited matchmaking.\n\n"
            "Use /find to start a new chat anytime."
        ),
    )
