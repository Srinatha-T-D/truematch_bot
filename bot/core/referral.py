# bot/core/referral.py

from datetime import datetime, timedelta, timezone
import logging

from bot.core.database import fetch_one, execute

logger = logging.getLogger(__name__)

REFERRAL_BONUS_DAYS = 3


async def apply_referral(new_user_id: int, referrer_id: int):
    """
    Apply referral bonus:
    - Only once
    - No self-referral
    - Referrer must exist
    """

    if new_user_id == referrer_id:
        return

    # Check if new user already has referrer
    existing = await fetch_one(
        "SELECT referred_by FROM users WHERE user_id = $1",
        new_user_id,
    )

    if not existing or existing["referred_by"]:
        return

    # Check referrer exists
    referrer = await fetch_one(
        "SELECT vip_until FROM users WHERE user_id = $1",
        referrer_id,
    )

    if not referrer:
        return

    now = datetime.now(timezone.utc)

    current_vip = referrer["vip_until"]

    if current_vip and current_vip > now:
        new_vip_until = current_vip + timedelta(days=REFERRAL_BONUS_DAYS)
    else:
        new_vip_until = now + timedelta(days=REFERRAL_BONUS_DAYS)

    # Update referrer VIP
    await execute(
        "UPDATE users SET vip_until = $1 WHERE user_id = $2",
        new_vip_until,
        referrer_id,
    )

    # Mark referral used
    await execute(
        "UPDATE users SET referred_by = $1 WHERE user_id = $2",
        referrer_id,
        new_user_id,
    )

    logger.info(
        f"REFERRAL APPLIED | referrer={referrer_id} | new_user={new_user_id} | bonus_days={REFERRAL_BONUS_DAYS}"
    )
