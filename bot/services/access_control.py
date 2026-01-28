# bot/services/access_control.py

from datetime import datetime, timezone
from typing import Literal

from bot.core.db import get_db
from bot.utils.logger import logger

UserTier = Literal["FREE", "VIP"]


class AccessControlService:
    """
    Central authority for access decisions.
    Cursor-type agnostic (tuple OR dict).
    """

    # =======================
    # INTERNAL HELPERS
    # =======================

    @staticmethod
    async def _has_valid_vip(user_id: int) -> bool:
        user_id = str(user_id)  # TEXT-safe

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT vip_until
                    FROM users
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
        except Exception:
            logger.exception(
                "Failed to check VIP status for user %s", user_id
            )
            return False
        finally:
            conn.close()

        if not row:
            return False

        # ✅ cursor-safe extraction
        vip_until = (
            row[0]
            if isinstance(row, (tuple, list))
            else row.get("vip_until")
        )

        if not vip_until:
            return False

        if vip_until.tzinfo is None:
            vip_until = vip_until.replace(tzinfo=timezone.utc)

        return vip_until >= datetime.now(timezone.utc)

    # =======================
    # PUBLIC API
    # =======================

    @staticmethod
    async def get_user_tier(user_id: int) -> UserTier:
        return "VIP" if await AccessControlService._has_valid_vip(user_id) else "FREE"

    @staticmethod
    async def can_access_vip_features(user_id: int) -> bool:
        return await AccessControlService._has_valid_vip(user_id)

    @staticmethod
    async def can_access_admin_features(user_id: int) -> bool:
        user_id = str(user_id)

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT is_admin
                    FROM users
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
        except Exception:
            logger.exception(
                "Failed to check admin status for user %s", user_id
            )
            return False
        finally:
            conn.close()

        if not row:
            return False

        # ✅ cursor-safe extraction
        is_admin = (
            row[0]
            if isinstance(row, (tuple, list))
            else row.get("is_admin")
        )

        return bool(is_admin)

    @staticmethod
    async def get_access_snapshot(user_id: int) -> dict:
        vip_active = await AccessControlService._has_valid_vip(user_id)

        return {
            "user_id": user_id,
            "tier": "VIP" if vip_active else "FREE",
            "vip_active": vip_active,
        }
