# bot/core/referral.py
# Referral logic (psycopg2-based, sync, FINAL)

import logging
from datetime import datetime, timedelta, timezone

from bot.core.db import get_db
from bot.config.settings import REFERRAL_BONUS_DAYS

logger = logging.getLogger(__name__)


async def apply_referral(new_user_id: str, referrer_id: str) -> bool:
    """
    Apply referral bonus:
    - Only once
    - No self-referral
    - Referrer must exist
    - Rewards VIP days to referrer

    IMPORTANT:
    user_id is TEXT everywhere in DB.
    """

    # 🚫 Prevent self-referral
    if not new_user_id or not referrer_id:
        return False

    if new_user_id == referrer_id:
        return False

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # 🔎 Check new user exists & not already referred
            cur.execute(
                "SELECT referred_by FROM users WHERE user_id = %s",
                (new_user_id,),
            )
            row = cur.fetchone()

            if not row or row["referred_by"] is not None:
                return False

            # 🔎 Check referrer exists
            cur.execute(
                "SELECT vip_until FROM users WHERE user_id = %s",
                (referrer_id,),
            )
            ref_row = cur.fetchone()

            if not ref_row:
                return False

            now = datetime.now(timezone.utc)
            current_vip_until = ref_row["vip_until"]

            # 🧮 Calculate new VIP expiry
            if current_vip_until and current_vip_until > now:
                new_vip_until = current_vip_until + timedelta(days=REFERRAL_BONUS_DAYS)
            else:
                new_vip_until = now + timedelta(days=REFERRAL_BONUS_DAYS)

            # ✅ Grant VIP bonus to referrer
            cur.execute(
                """
                UPDATE users
                SET vip_until = %s
                WHERE user_id = %s
                """,
                (new_vip_until, referrer_id),
            )

            # ✅ Mark referral used
            cur.execute(
                """
                UPDATE users
                SET referred_by = %s
                WHERE user_id = %s
                """,
                (referrer_id, new_user_id),
            )

        conn.commit()

        logger.info(
            "REFERRAL APPLIED | referrer=%s | new_user=%s | bonus_days=%s",
            referrer_id,
            new_user_id,
            REFERRAL_BONUS_DAYS,
        )

        return True

    except Exception:
        logger.exception(
            "REFERRAL FAILED | referrer=%s | new_user=%s",
            referrer_id,
            new_user_id,
        )
        return False

    finally:
        conn.close()
