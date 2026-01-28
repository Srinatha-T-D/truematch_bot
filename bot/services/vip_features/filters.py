# bot/services/vip_features/filters.py
# VIP Filters — persistence only (NO matchmaking logic)

from typing import Optional, Dict
from bot.core.db import get_db
from bot.utils.logger import logger


class VipFiltersService:
    """
    Stores and retrieves VIP matchmaking preferences.
    Matching logic MUST stay in core.matchmaking.
    """

    # =========================
    # SAVE / UPDATE FILTERS
    # =========================

    @staticmethod
    def set_age_range(
        user_id: int,
        age_min: Optional[int],
        age_max: Optional[int],
    ) -> None:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET age_min=%s,
                        age_max=%s
                    WHERE user_id=%s
                    """,
                    (age_min, age_max, user_id),
                )
                conn.commit()
        finally:
            conn.close()

        logger.info(
            "[VIP FILTERS] user=%s age_min=%s age_max=%s",
            user_id, age_min, age_max,
        )

    @staticmethod
    def set_state(user_id: int, state: Optional[str]) -> None:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET state=%s
                    WHERE user_id=%s
                    """,
                    (state, user_id),
                )
                conn.commit()
        finally:
            conn.close()

        logger.info("[VIP FILTERS] user=%s state=%s", user_id, state)

    @staticmethod
    def set_language(user_id: int, language: Optional[str]) -> None:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET language=%s
                    WHERE user_id=%s
                    """,
                    (language, user_id),
                )
                conn.commit()
        finally:
            conn.close()

        logger.info("[VIP FILTERS] user=%s language=%s", user_id, language)

    @staticmethod
    def set_verified_only(user_id: int, enabled: bool) -> None:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET verified_only=%s
                    WHERE user_id=%s
                    """,
                    (enabled, user_id),
                )
                conn.commit()
        finally:
            conn.close()

        logger.info(
            "[VIP FILTERS] user=%s verified_only=%s",
            user_id, enabled,
        )

    # =========================
    # FETCH FILTERS (OPTIONAL)
    # =========================

    @staticmethod
    def get_filters(user_id: int) -> Dict[str, Optional[object]]:
        """
        Used only for UI display or debugging.
        Core matchmaking reads directly from DB.
        """
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT age_min, age_max, state, language, verified_only
                    FROM users
                    WHERE user_id=%s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            return {}

        return {
            "age_min": row[0],
            "age_max": row[1],
            "state": row[2],
            "language": row[3],
            "verified_only": row[4],
        }

    # =========================
    # RESET ALL FILTERS
    # =========================

    @staticmethod
    def reset_all(user_id: int) -> None:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET age_min=NULL,
                        age_max=NULL,
                        state=NULL,
                        language=NULL,
                        verified_only=FALSE
                    WHERE user_id=%s
                    """,
                    (user_id,),
                )
                conn.commit()
        finally:
            conn.close()

        logger.info("[VIP FILTERS] user=%s filters reset", user_id)
