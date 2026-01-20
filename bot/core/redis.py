# bot/core/redis.py

import logging
import redis.asyncio as redis

from bot.config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB

logger = logging.getLogger(__name__)

_redis: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """
    Create or return Redis connection
    """
    global _redis

    if _redis is None:
        logger.info("🔌 Connecting to Redis")

        _redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )

    return _redis
