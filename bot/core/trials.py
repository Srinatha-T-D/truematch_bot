# bot/core/trials.py

import logging
from datetime import date

from bot.config.settings import (
    GLOBAL_FREE_START,
    GLOBAL_FREE_END,
    FREE_TRIAL_COUNT,
)

from bot.core.users import (
    get_or_create_user,
    decrement_trial,
    is_vip_user,
)

logger = logging.getLogger(__name__)


async def can_user_chat(user_id: int) -> bool:
    """
    Central access control for chatting.

    Rules:
    1. Global free window → ALWAYS allow
    2. VIP user → allow
    3. Trials left → allow and decrement
    4. Otherwise → block
    """

    today = date.today()

    # 🔥 GLOBAL FREE WINDOW (HIGHEST PRIORITY)
    if GLOBAL_FREE_START <= today <= GLOBAL_FREE_END:
        logger.info(f"User {user_id} allowed (GLOBAL FREE)")
        return True

    # Ensure user exists
    user = await get_or_create_user(user_id)

    # ⭐ VIP BYPASS
    if await is_vip_user(user_id):
        logger.info(f"User {user_id} allowed (VIP)")
        return True

    # 🎟️ FREE TRIAL
    if user["trials_left"] > 0:
        await decrement_trial(user_id)
        logger.info(
            f"User {user_id} allowed (trial used, left={user['trials_left'] - 1})"
        )
        return True

    # 🚫 BLOCK
    logger.info(f"User {user_id} blocked (no access)")
    return False
