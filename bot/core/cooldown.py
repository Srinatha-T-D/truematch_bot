# bot/core/cooldown.py

import time
import logging
from bot.core.redis import get_redis

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 10
KEY_PREFIX = "cooldown:enqueue"


async def is_on_cooldown(user_id: int) -> int:
    """
    Returns remaining cooldown seconds if active, else 0
    """
    redis = await get_redis()
    key = f"{KEY_PREFIX}:{user_id}"

    last_ts = await redis.get(key)
    if not last_ts:
        return 0

    elapsed = time.time() - float(last_ts)
    remaining = COOLDOWN_SECONDS - int(elapsed)

    return max(0, remaining)


async def set_cooldown(user_id: int):
    redis = await get_redis()
    key = f"{KEY_PREFIX}:{user_id}"

    await redis.set(
        key,
        time.time(),
        ex=COOLDOWN_SECONDS,
    )

    logger.info(f"Cooldown set for user {user_id}")
