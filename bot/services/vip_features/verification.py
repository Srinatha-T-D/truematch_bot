# bot/services/vip_features/verification.py

from typing import Optional
from bot.core.db import get_db
from bot.utils.logger import logger


class VipVerificationService:
    """
    Profile verification service.
    Privacy-safe: no documents, no chats, no identities.
    Admin-controlled approval only.
    Uses synchronous psycopg2 safely inside async handlers.
    """

    # -----------------------------
    # USER SIDE
    # -----------------------------

    @staticmethod
    async def is_verified(user_id: int) -> bool:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT is_verified
                    FROM users
                    WHERE telegram_id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()

            return bool(row and row[0])

        except Exception:
            logger.exception(
                "Failed to check verification status for user %s",
                user_id,
            )
            return False
        finally:
            conn.close()

    @staticmethod
    async def request_verification(user_id: int) -> bool:
        """
        User requests verification.
        We only log intent; no auto-approval.
        """
        logger.info("[VERIFY REQUEST] User %s requested verification", user_id)
        return True

    # -----------------------------
    # ADMIN SIDE
    # -----------------------------

    @staticmethod
    async def approve_verification(user_id: int) -> None:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET is_verified = TRUE
                    WHERE telegram_id = %s
                    """,
                    (user_id,),
                )
                conn.commit()

            logger.info("[VERIFY APPROVED] User %s", user_id)

        except Exception:
            logger.exception(
                "Failed to approve verification for user %s",
                user_id,
            )
        finally:
            conn.close()

    @staticmethod
    async def revoke_verification(user_id: int) -> None:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET is_verified = FALSE
                    WHERE telegram_id = %s
                    """,
                    (user_id,),
                )
                conn.commit()

            logger.warning("[VERIFY REVOKED] User %s", user_id)

        except Exception:
            logger.exception(
                "Failed to revoke verification for user %s",
                user_id,
            )
        finally:
            conn.close()

    # -----------------------------
    # ADMIN HELPERS
    # -----------------------------

    @staticmethod
    async def get_verification_status(user_id: int) -> Optional[bool]:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT is_verified
                    FROM users
                    WHERE telegram_id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()

            return row[0] if row else None

        except Exception:
            logger.exception(
                "Failed to fetch verification status for user %s",
                user_id,
            )
            return None
        finally:
            conn.close()
