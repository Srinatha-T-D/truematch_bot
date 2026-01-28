# bot/core/recovery.py
# Crash / restart recovery logic

import logging
from bot.core.redis import get_redis
from bot.core.matchmaking import ACTIVE_CHATS

logger = logging.getLogger(__name__)


async def crash_recovery():
    """
    Clean up stale matchmaking state after bot restart.
    This prevents ghost queues and invalid in-memory sessions.
    """

    logger.info("🧯 Starting crash recovery")

    # 1️⃣ Clear in-memory active chats
    ACTIVE_CHATS.clear()
    logger.info("🧹 Cleared ACTIVE_CHATS (in-memory)")

    # 2️⃣ Clear Redis matchmaking queues safely
    redis = await get_redis()

    try:
        keys = await redis.keys("queue:*")
        if not keys:
            logger.info("ℹ️ No Redis queues found")
        else:
            for key in keys:
                await redis.delete(key)
                logger.info("🧹 Cleared Redis queue: %s", key)
    except Exception as e:
        # Recovery must NEVER crash the bot
        logger.error("❌ Error during Redis queue cleanup: %s", e)

    logger.info("✅ Crash recovery cleanup completed")
