# bot/core/users.py
# User-level helpers built strictly on top of core.db
# FINAL – aligned with registration + matchmaking core logic

import logging
from datetime import datetime, timezone
from typing import Optional, Dict

from bot.core.db import (
    ensure_user,
    get_user,
    is_hard_banned,
    is_shadow_banned,
    is_vip,
    set_vip_until,
    get_trials_left,
    consume_trial,
    update_last_active,
)
from bot.config.settings import FREE_TRIAL_COUNT

logger = logging.getLogger(__name__)


# =========================
# USER BOOTSTRAP
# =========================

def get_or_create_user(user_id: int, username: Optional[str] = None) -> Dict:
    """
    Fetch user from DB or create if not exists.
    user_id is stored as TEXT.
    """
    user_id = str(user_id)

    user = get_user(user_id)
    if user:
        return dict(user)

    ensure_user(user_id, username)

    logger.info("Created new user %s", user_id)

    return {
        "user_id": user_id,
        "trials_left": FREE_TRIAL_COUNT,
        "vip_until": None,
        "is_banned": False,
        "is_verified": False,
    }


def get_user_by_id(user_id: int | str) -> Dict:
    """
    Fetch full user row as dict.
    Returns empty dict if user does not exist.
    """
    user = get_user(str(user_id))
    return dict(user) if user else {}


# =========================
# REGISTRATION HELPERS
# =========================

def update_user_preferences(
    user_id: int | str,
    *,
    gender: Optional[str] = None,
    looking_for: Optional[str] = None,
) -> None:
    """
    Update registration preferences.
    Only updates provided fields.
    """
    fields = []
    values = []

    if gender is not None:
        fields.append("gender = %s")
        values.append(gender)

    if looking_for is not None:
        fields.append("looking_for = %s")
        values.append(looking_for)

    if not fields:
        return

    query = f"""
        UPDATE users
        SET {", ".join(fields)}
        WHERE user_id = %s
    """
    values.append(str(user_id))

    from bot.core.db import get_db
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            conn.commit()
    finally:
        conn.close()

    logger.info(
        "Updated registration preferences for user %s (gender=%s, looking_for=%s)",
        user_id, gender, looking_for
    )


def is_user_registered(user_id: int | str) -> bool:
    """
    User is considered registered only if
    gender AND looking_for are set.
    """
    user = get_user_by_id(user_id)
    return bool(user.get("gender") and user.get("looking_for"))


# =========================
# BAN CHECKS
# =========================

def user_is_blocked(user_id: int) -> bool:
    """
    Hard ban check (absolute block)
    """
    return is_hard_banned(str(user_id))


def user_is_shadow_banned(user_id: int) -> bool:
    """
    Shadow ban check (exclude from matchmaking)
    """
    return is_shadow_banned(str(user_id))


# =========================
# TRIAL SYSTEM
# =========================

def get_remaining_trials(user_id: int) -> int:
    """
    Returns remaining free trials
    """
    return get_trials_left(str(user_id))


def consume_free_trial(user_id: int) -> bool:
    """
    Consume one free trial if available.
    Returns True if consumed, False otherwise.
    """
    return consume_trial(str(user_id))


# =========================
# VIP SYSTEM
# =========================

def is_vip_user(user_id: int) -> bool:
    """
    Check if user has active VIP
    """
    return is_vip(str(user_id))


def grant_vip(user_id: int, vip_until: datetime):
    """
    Grant VIP access until given datetime
    """
    if vip_until.tzinfo is None:
        vip_until = vip_until.replace(tzinfo=timezone.utc)

    set_vip_until(str(user_id), vip_until)

    logger.info("User %s granted VIP until %s", user_id, vip_until)


# =========================
# ACTIVITY
# =========================

def mark_user_active(user_id: int):
    """
    Update last_active timestamp
    """
    update_last_active(str(user_id))
