# bot/core/matchmaking.py

import logging
from typing import Dict, Tuple

from bot.core.redis import get_redis
from bot.utils.keyboards import disconnect_keyboard
from bot.core.chat_logger import create_chat_session, end_chat_session

logger = logging.getLogger(__name__)

# user_id -> (partner_user_id, partner_chat_id, session_id)
ACTIVE_CHATS: Dict[int, Tuple[int, int, str]] = {}


def _queue_key(intent: str) -> str:
    return f"queue:{intent}"


async def add_to_queue(user_id: int, chat_id: int, intent: str, context):
    redis = await get_redis()
    queue_key = _queue_key(intent)

    # 🚫 Already in an active chat
    if user_id in ACTIVE_CHATS:
        return

    # 🚫 Prevent duplicate queue entry
    queue_items = await redis.lrange(queue_key, 0, -1)
    for item in queue_items:
        q_user_id, _ = map(int, item.split(":"))
        if q_user_id == user_id:
            logger.info(f"User {user_id} already in queue, skipping")
            return

    partner = await redis.lpop(queue_key)

    if partner:
        partner_id, partner_chat_id = map(int, partner.split(":"))

        # 🚫 Prevent self-match
        if partner_id == user_id:
            logger.warning(f"Prevented self-match for user {user_id}")
            await redis.rpush(queue_key, partner)
            return

        await _match_users(
            user_id,
            chat_id,
            partner_id,
            partner_chat_id,
            context,
        )
        return

    await redis.rpush(queue_key, f"{user_id}:{chat_id}")
    logger.info(f"User {user_id} queued under intent '{intent}'")


async def _match_users(
    user_id: int,
    chat_id: int,
    partner_id: int,
    partner_chat_id: int,
    context,
):
    # 🔐 Create chat session for admin audit (14-day retention)
    session_id = await create_chat_session(user_id, partner_id)

    ACTIVE_CHATS[user_id] = (partner_id, partner_chat_id, session_id)
    ACTIVE_CHATS[partner_id] = (user_id, chat_id, session_id)

    logger.info(f"Matched users {user_id} <-> {partner_id} | session={session_id}")

    await context.bot.send_message(
        chat_id=chat_id,
        text="🎉 *You are now connected anonymously!*",
        reply_markup=disconnect_keyboard(),
        parse_mode="Markdown",
    )

    await context.bot.send_message(
        chat_id=partner_chat_id,
        text="🎉 *You are now connected anonymously!*",
        reply_markup=disconnect_keyboard(),
        parse_mode="Markdown",
    )


def get_partner(user_id: int):
    return ACTIVE_CHATS.get(user_id)


def disconnect_users(user_id: int):
    chat = ACTIVE_CHATS.pop(user_id, None)
    if not chat:
        return

    partner_id, _, session_id = chat
    ACTIVE_CHATS.pop(partner_id, None)

    # 🔐 Close chat session safely (async, non-blocking)
    import asyncio
    asyncio.create_task(end_chat_session(session_id))

    logger.info(f"Chat ended | users={user_id},{partner_id} | session={session_id}")
