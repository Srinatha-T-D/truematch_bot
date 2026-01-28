# bot/core/trials.py
# Centralized trial + global free window logic
# NO Telegram imports, NO DB access directly

import logging
from datetime import date

from bot.config.settings import (
    GLOBAL_FREE_START,
    GLOBAL_FREE_END,
)

from bot.core.users import (
    get_or_create_user,
    get_remaining_trials,
    consume_free_trial,
    is_vip_user,
)

logger = logging.getLogger(__name__)


def is_global_free_active() -> bool:
    """
    Check if global free window is active.
    """
    today = date.today()
    return GLOBAL_FREE_START <= today <= GLOBAL_FREE_END


def can_user_chat(user_id: int) -> bool:
    """
    Central access control for chatting.

    Rules (in order):
    1. Global free window → ALWAYS allow (no consumption)
    2. VIP user → allow (no consumption)
    3. Free trials available → allow (consume 1)
    4. Otherwise → block
    """

    user_id = int(user_id)

    # Ensure user exists (safe no-op if already exists)
    get_or_create_user(user_id)

    # 🔥 GLOBAL FREE WINDOW (highest priority)
    if is_global_free_active():
        logger.info("User %s allowed (GLOBAL FREE WINDOW)", user_id)
        return True

    # ⭐ VIP BYPASS
    if is_vip_user(user_id):
        logger.info("User %s allowed (VIP)", user_id)
        return True

    # 🎟️ FREE TRIAL
    trials_left = get_remaining_trials(user_id)
    if trials_left > 0:
        consumed = consume_free_trial(user_id)
        if consumed:
            logger.info(
                "User %s allowed (trial consumed, remaining=%s)",
                user_id,
                trials_left - 1,
            )
            return True

    # 🚫 BLOCK
    logger.info("User %s blocked (no access)", user_id)
    return False
