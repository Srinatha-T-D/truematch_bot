# bot/handlers/stop.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import get_partner, disconnect_users
from bot.core.redis import get_redis

logger = logging.getLogger(__name__)


async def _remove_from_all_queues(user_id: int):
    redis = await get_redis()
    keys = await redis.keys("queue:*")

    for key in keys:
        items = await redis.lrange(key, 0, -1)
        for item in items:
            q_user_id, _ = map(int, item.split(":"))
            if q_user_id == user_id:
                await redis.lrem(key, 1, item)
                logger.info(f"User {user_id} removed from queue {key}")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    partner = get_partner(user.id)

    # ==========================
    # DISCONNECT BOTH USERS
    # ==========================
    if partner:
        partner_id, partner_chat_id = partner

        # Clear active chat mapping
        disconnect_users(user.id)

        # Notify both sides
        await context.bot.send_message(
            chat_id=chat_id,
            text="🛑 You have stopped the chat.",
        )

        await context.bot.send_message(
            chat_id=partner_chat_id,
            text="❌ Your partner has stopped the chat.",
        )

        # Remove both users from queues
        await _remove_from_all_queues(user.id)
        await _remove_from_all_queues(partner_id)

        logger.info(
            f"Chat stopped | user={user.id} partner={partner_id}"
        )

    else:
        # Not in chat — still cleanup
        await _remove_from_all_queues(user.id)

        await context.bot.send_message(
            chat_id=chat_id,
            text="🛑 You have stopped matchmaking.",
        )

    # ==========================
    # CLEAR SESSION STATE
    # ==========================
    context.user_data.clear()
