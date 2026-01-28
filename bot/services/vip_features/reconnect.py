# bot/services/vip_features/reconnect.py

from typing import List

from bot.core.db import get_db
from bot.utils.logger import logger


class VipReconnectService:
    """
    VIP Reconnect service.

    Responsibilities:
    - Check VIP access
    - Store recent anonymous connections
    - Fetch reconnect candidates (Postgres-safe)
    """

    MAX_HISTORY = 5

    # -------------------------
    # ACCESS CHECK
    # -------------------------

    @staticmethod
    def can_reconnect(user_id: int) -> bool:
        query = """
            SELECT vip_until
            FROM users
            WHERE user_id = %s
        """

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (str(user_id),))
                row = cur.fetchone()
            return bool(row and row[0])
        except Exception:
            logger.exception(
                "[VIP RECONNECT] Access check failed for user %s",
                user_id,
            )
            return False
        finally:
            conn.close()

    # -------------------------
    # HISTORY STORE
    # -------------------------

    @staticmethod
    def save_connection(user_id: str, partner_id: str):
        """
        Save anonymous connection (both directions).
        """
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO chat_history (user_id, partner_id)
                    VALUES (%s, %s), (%s, %s)
                    """,
                    (user_id, partner_id, partner_id, user_id),
                )
            conn.commit()
        finally:
            conn.close()

    # -------------------------
    # HISTORY FETCH (FIXED)
    # -------------------------

    @staticmethod
    def get_recent_partners(user_id: int) -> List[str]:
        """
        Return most recent distinct partners, ordered by last interaction.
        Postgres-safe DISTINCT handling.
        """
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT partner_id
                    FROM chat_history
                    WHERE user_id = %s
                    GROUP BY partner_id
                    ORDER BY MAX(ended_at) DESC
                    LIMIT %s
                    """,
                    (str(user_id), VipReconnectService.MAX_HISTORY),
                )
                rows = cur.fetchall()
        except Exception:
            logger.exception(
                "[VIP RECONNECT] Failed fetching history for user %s",
                user_id,
            )
            return []
        finally:
            conn.close()

        return [r[0] for r in rows]

    # -------------------------
    # LOGGING
    # -------------------------

    @staticmethod
    def log_reconnect(user_id: int, success: bool):
        if success:
            logger.info("[VIP RECONNECT] User %s reconnected", user_id)
        else:
            logger.warning("[VIP RECONNECT] User %s reconnect denied", user_id)
