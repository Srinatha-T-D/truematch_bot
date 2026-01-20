# bot/core/users.py

import logging
from datetime import datetime

from bot.core.database import fetch_one, execute
from bot.config.settings import FREE_TRIAL_COUNT

logger = logging.getLogger(__name__)


async def get_or_create_user(user_id: int) -> dict:
    """
    Fetch user from DB or create if not exists
    """

    user = await fetch_one(
        """
        SELECT user_id, trials_left, vip_until
        FROM users
        WHERE user_id = $1
        """,
        (user_id,),
    )

    if user:
        return user

    await execute(
        """
        INSERT INTO users (user_id, trials_left, vip_until, created_at)
        VALUES ($1, $2, NULL, NOW())
        """,
        (user_id, FREE_TRIAL_COUNT),
    )

    logger.info(f"Created new user {user_id}")

    return {
        "user_id": user_id,
        "trials_left": FREE_TRIAL_COUNT,
        "vip_until": None,
    }


async def decrement_trial(user_id: int):
    """
    Decrease trial count by 1
    """

    await execute(
        """
        UPDATE users
        SET trials_left = trials_left - 1
        WHERE user_id = $1 AND trials_left > 0
        """,
        (user_id,),
    )


async def is_vip_user(user_id: int) -> bool:
    """
    Check if user has active VIP
    """

    row = await fetch_one(
        """
        SELECT vip_until
        FROM users
        WHERE user_id = $1
        """,
        (user_id,),
    )

    if not row or not row["vip_until"]:
        return False

    return row["vip_until"] > datetime.utcnow()


async def grant_vip(user_id: int, vip_until):
    """
    Grant VIP access until given datetime
    """

    await execute(
        """
        UPDATE users
        SET vip_until = $1
        WHERE user_id = $2
        """,
        (vip_until, user_id),
    )

    logger.info(f"User {user_id} granted VIP until {vip_until}")
