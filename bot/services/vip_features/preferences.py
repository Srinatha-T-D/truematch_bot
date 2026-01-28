from typing import Dict, List, Optional

from bot.core.db import get_db
from bot.utils.logger import logger


class VipPreferencesService:
    """
    VIP Preferences service.
    Preferences do NOT exclude users.
    They only influence ranking / scoring.
    """

    # -----------------------------
    # SAVE / UPDATE PREFERENCES
    # -----------------------------
    @staticmethod
    def save_preferences(
        user_id: int,
        prefer_same_language: Optional[bool] = None,
        prefer_verified_users: Optional[bool] = None,
        prefer_vip_users: Optional[bool] = None,
    ) -> None:
        fields = []
        values = []

        if prefer_same_language is not None:
            fields.append("prefer_same_language = %s")
            values.append(prefer_same_language)

        if prefer_verified_users is not None:
            fields.append("prefer_verified_users = %s")
            values.append(prefer_verified_users)

        if prefer_vip_users is not None:
            fields.append("prefer_vip_users = %s")
            values.append(prefer_vip_users)

        if not fields:
            return

        query = f"""
            UPDATE users
            SET {", ".join(fields)}
            WHERE user_id = %s::text
        """
        values.append(str(user_id))  # 🔑 CAST FIX

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(query, values)
            conn.commit()
        finally:
            conn.close()

        logger.info("[VIP PREF] Updated preferences for user %s", user_id)

    # -----------------------------
    # FETCH PREFERENCES
    # -----------------------------
    @staticmethod
    def get_preferences(user_id: int) -> Dict:
        query = """
            SELECT
                prefer_same_language,
                prefer_verified_users,
                prefer_vip_users
            FROM users
            WHERE user_id = %s::text
        """

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (str(user_id),))
                row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            return {}

        return {
            "prefer_same_language": row[0],
            "prefer_verified_users": row[1],
            "prefer_vip_users": row[2],
        }

    # -----------------------------
    # SCORE CANDIDATES
    # -----------------------------
    @staticmethod
    def score_candidates(
        user_id: int,
        candidate_user_ids: List[int],
    ) -> List[int]:
        if not candidate_user_ids:
            return []

        preferences = VipPreferencesService.get_preferences(user_id)
        if not preferences:
            return candidate_user_ids

        query = """
            SELECT
                user_id,
                language,
                is_verified,
                vip_until
            FROM users
            WHERE user_id = ANY(%s)
        """

        # convert IDs to TEXT for Postgres
        candidate_ids = [str(uid) for uid in candidate_user_ids]

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (candidate_ids,))
                rows = cur.fetchall()
        finally:
            conn.close()

        scored = []

        for uid, language, is_verified, vip_until in rows:
            score = 0

            if preferences.get("prefer_same_language") and language:
                score += 10

            if preferences.get("prefer_verified_users") and is_verified:
                score += 15

            if preferences.get("prefer_vip_users") and vip_until:
                score += 8

            scored.append((uid, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        logger.info(
            "[VIP PREF] Ranked %d candidates for user %s",
            len(scored),
            user_id,
        )

        return [uid for uid, _ in scored]
