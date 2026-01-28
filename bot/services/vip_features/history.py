# bot/services/vip_features/history.py

from datetime import timedelta
from typing import Dict

from bot.core.db import get_db
from bot.utils.logger import logger


class VipHistoryService:
    """
    Privacy-safe connection insights.
    Uses chat_session_stats table only.
    No identities, no messages.
    """

    # -----------------------------
    # BASIC COUNTS
    # -----------------------------

    @staticmethod
    async def get_total_chats(user_id: int) -> int:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) 
                    FROM chat_session_stats
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                return cur.fetchone()[0]
        except Exception:
            logger.exception("Failed to fetch total chats for user %s", user_id)
            return 0
        finally:
            conn.close()

    # -----------------------------
    # TIME METRICS
    # -----------------------------

    @staticmethod
    async def get_time_stats(user_id: int) -> Dict:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT started_at, ended_at
                    FROM chat_session_stats
                    WHERE user_id = %s
                      AND ended_at IS NOT NULL
                    """,
                    (user_id,),
                )
                rows = cur.fetchall()

            total_duration = timedelta()
            longest = timedelta()

            for started_at, ended_at in rows:
                duration = ended_at - started_at
                total_duration += duration
                if duration > longest:
                    longest = duration

            avg = total_duration / len(rows) if rows else timedelta()

            return {
                "total_time": total_duration,
                "average_time": avg,
                "longest_time": longest,
            }

        except Exception:
            logger.exception("Failed to fetch time stats for user %s", user_id)
            return {
                "total_time": timedelta(),
                "average_time": timedelta(),
                "longest_time": timedelta(),
            }
        finally:
            conn.close()

    # -----------------------------
    # PARTNER TYPE BREAKDOWN
    # -----------------------------

    @staticmethod
    async def get_partner_type_stats(user_id: int) -> Dict:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE partner_verified = TRUE),
                        COUNT(*) FILTER (WHERE partner_verified = FALSE),
                        COUNT(*) FILTER (WHERE partner_vip = TRUE),
                        COUNT(*) FILTER (WHERE partner_vip = FALSE)
                    FROM chat_session_stats
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()

            return {
                "verified_count": row[0],
                "non_verified_count": row[1],
                "vip_count": row[2],
                "non_vip_count": row[3],
            }

        except Exception:
            logger.exception("Failed to fetch partner stats for user %s", user_id)
            return {}
        finally:
            conn.close()

    # -----------------------------
    # GEOGRAPHY & LANGUAGE
    # -----------------------------

    @staticmethod
    async def get_geo_language_stats(user_id: int) -> Dict:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT partner_state, partner_language, COUNT(*)
                    FROM chat_session_stats
                    WHERE user_id = %s
                    GROUP BY partner_state, partner_language
                    """,
                    (user_id,),
                )
                rows = cur.fetchall()

            state_stats = {}
            language_stats = {}

            for state, language, count in rows:
                if state:
                    state_stats[state] = state_stats.get(state, 0) + count
                if language:
                    language_stats[language] = language_stats.get(language, 0) + count

            return {
                "states": state_stats,
                "languages": language_stats,
            }

        except Exception:
            logger.exception("Failed to fetch geo/language stats for user %s", user_id)
            return {"states": {}, "languages": {}}
        finally:
            conn.close()

    # -----------------------------
    # QUALITY SIGNALS
    # -----------------------------

    @staticmethod
    async def get_quality_metrics(user_id: int) -> Dict:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT started_at, ended_at
                    FROM chat_session_stats
                    WHERE user_id = %s
                      AND ended_at IS NOT NULL
                    """,
                    (user_id,),
                )
                rows = cur.fetchall()

            long_chats = 0
            short_chats = 0

            for started_at, ended_at in rows:
                duration = ended_at - started_at
                if duration >= timedelta(minutes=10):
                    long_chats += 1
                else:
                    short_chats += 1

            total = len(rows)

            return {
                "long_chat_percent": (long_chats / total * 100) if total else 0,
                "short_chat_percent": (short_chats / total * 100) if total else 0,
            }

        except Exception:
            logger.exception("Failed to fetch quality metrics for user %s", user_id)
            return {"long_chat_percent": 0, "short_chat_percent": 0}
        finally:
            conn.close()

    # -----------------------------
    # MASTER INSIGHTS
    # -----------------------------

    @staticmethod
    async def get_full_insights(user_id: int) -> Dict:
        """
        Single call for VIP insights dashboard.
        """
        insights = {
            "total_chats": await VipHistoryService.get_total_chats(user_id),
            "time": await VipHistoryService.get_time_stats(user_id),
            "partners": await VipHistoryService.get_partner_type_stats(user_id),
            "geo_language": await VipHistoryService.get_geo_language_stats(user_id),
            "quality": await VipHistoryService.get_quality_metrics(user_id),
        }

        logger.info("[VIP INSIGHTS] Generated for user %s", user_id)
        return insights
