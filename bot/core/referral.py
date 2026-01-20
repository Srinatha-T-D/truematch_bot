# bot/core/referral.py

from datetime import datetime, timedelta, timezone
import logging

from bot.core.database import fetch_one, execute

logger = logging.getLogger(__name__)

# 🎁 Referral reward (VIP days)
from bot.config.settings import REFERRAL_BONUS_DAYS


async def apply_referral(new_user_id: int, referrer_id: int) -> bool:
    """
    Apply referral bonus:
    - Only once
    - No self-referral
    - Referrer must exist
    - Rewards VIP days to referrer

    Returns:
        True  -> referral applied
        False -> referral ignored
    """

    # 🚫 Prevent self-referral
    if new_user_id == referrer_id:
        return False

    # 🔎 Check if new user already has a referrer
    existing = await fetch_one(
        "SELECT referred_by FROM users WHERE user_id = $1",
        new_user_id,
    )

    if not existing or existing["referred_by"]:
        return False

    # 🔎 Check referrer exists
    referrer = await fetch_one(
        "SELECT vip_until FROM users WHERE user_id = $1",
        referrer_id,
    )

    if not referrer:
        return False

    now = datetime.now(timezone.utc)
    current_vip = referrer["vip_until"]

    # 🧮 Calculate new VIP expiry
    if current_vip and current_vip > now:
        new_vip_until = current_vip + timedelta(days=REFERRAL_BONUS_DAYS)
    else:
        new_vip_until = now + timedelta(days=REFERRAL_BONUS_DAYS)

    # ✅ Update referrer VIP
    await execute(
        "UPDATE users SET vip_until = $1 WHERE user_id = $2",
        new_vip_until,
        referrer_id,
    )

    # ✅ Mark referral used
    await execute(
        "UPDATE users SET referred_by = $1 WHERE user_id = $2",
        referrer_id,
        new_user_id,
    )

    logger.info(
        f"REFERRAL APPLIED | referrer={referrer_id} | "
        f"new_user={new_user_id} | bonus_days={REFERRAL_BONUS_DAYS}"
    )

    return True
