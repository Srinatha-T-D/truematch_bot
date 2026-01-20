# bot/core/recovery.py

import logging
from bot.core.redis import get_redis
from bot.core.matchmaking import ACTIVE_CHATS

logger = logging.getLogger(__name__)


async def crash_recovery():
    """
    Clean up stale matchmaking state after bot restart.
    """
    # 1️⃣ Clear in-memory active chats
    ACTIVE_CHATS.clear()
    logger.info("🧹 Cleared ACTIVE_CHATS (memory)")

    # 2️⃣ Clear Redis matchmaking queues
    redis = await get_redis()
    keys = await redis.keys("queue:*")

    for key in keys:
        await redis.delete(key)
        logger.info(f"🧹 Cleared Redis queue: {key}")

    logger.info("✅ Crash recovery cleanup completed")
