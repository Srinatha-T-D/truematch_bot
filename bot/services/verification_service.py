# bot/services/verification_service.py
# Handles persistence of verification requests

from bot.core.db import get_db
from bot.utils.logger import logger


class VerificationService:
    @staticmethod
    def has_pending_request(user_id: int) -> bool:
        query = """
            SELECT 1
            FROM verification_requests
            WHERE user_id = %s
              AND status = 'pending'
            LIMIT 1
        """

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (str(user_id),))
                return cur.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def create_request(
        user_id: int,
        full_name: str,
        gender: str,
        contact: str,
    ) -> None:
        query = """
            INSERT INTO verification_requests
            (user_id, full_name, gender, contact)
            VALUES (%s, %s, %s, %s)
        """

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (str(user_id), full_name, gender, contact),
                )
            conn.commit()
        finally:
            conn.close()

        logger.info(
            "[VERIFY] verification request created user=%s", user_id
        )
