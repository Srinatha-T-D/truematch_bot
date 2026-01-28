from datetime import datetime, timezone

from bot.core.db import get_db
from bot.utils.logger import logger


class VipSessionLogger:
    """
    Writes privacy-safe analytics rows on chat end.
    """

    @staticmethod
    async def log_session(
        user_id: int,
        partner_id: int,
        started_at: datetime,
        ended_at: datetime,
    ):
        """
        Create one analytics row for ONE user.
        Must be called twice (for both users).
        """
        query = """
            INSERT INTO chat_session_stats (
                user_id,
                partner_vip,
                partner_verified,
                partner_state,
                partner_language,
                started_at,
                ended_at
            )
            SELECT
                $1,
                (vip_until >= NOW()),
                is_verified,
                state,
                language,
                $2,
                $3
            FROM users
            WHERE telegram_id = $4
        """

        async with get_db() as conn:
            await conn.execute(
                query,
                user_id,
                started_at,
                ended_at,
                partner_id
            )

        logger.info(
            f"[SESSION STATS] user={user_id} partner={partner_id} "
            f"duration={(ended_at - started_at).total_seconds()}s"
        )
