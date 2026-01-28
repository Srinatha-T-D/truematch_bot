# bot/core/vip.py
# Authoritative VIP & access decision logic

from bot.core.db import (
    is_vip,
    get_trials_left,
    consume_trial,
)
import logging

logger = logging.getLogger(__name__)


# =========================
# ACCESS DECISIONS
# =========================

def can_user_chat(user_id: int) -> bool:
    """
    Returns True if user can start a chat.
    VIP users are always allowed.
    Free users must have trials_left > 0.
    """
    user_id = str(user_id)

    if is_vip(user_id):
        return True

    return get_trials_left(user_id) > 0


def consume_access(user_id: int) -> bool:
    """
    Consume access for a chat session.
    - VIP users: nothing consumed
    - Free users: 1 trial consumed
    Returns True if access granted, False otherwise.
    """
    user_id = str(user_id)

    if is_vip(user_id):
        return True

    consumed = consume_trial(user_id)
    if not consumed:
        logger.info("User %s has no trials left", user_id)

    return consumed


# =========================
# INFO HELPERS
# =========================

def get_access_status(user_id: int) -> dict:
    """
    Returns current access status for UI/handlers.
    """
    user_id = str(user_id)

    vip = is_vip(user_id)
    trials_left = get_trials_left(user_id)

    return {
        "is_vip": vip,
        "trials_left": trials_left,
        "can_chat": vip or trials_left > 0,
    }
