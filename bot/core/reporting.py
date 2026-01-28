# bot/core/reporting.py
# User report handling (psycopg2-based, FINAL)

import logging
from datetime import datetime, timezone

from bot.core.db import get_db

logger = logging.getLogger(__name__)


def file_report(
    reporter_id: int,
    reported_user_id: int,
    session_id: str,
    reason: str,
):
    """
    File a user report.
    Messages are NOT stored.
    Only metadata is recorded for moderation.
    """

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reports (
                    reporter_id,
                    reported_user_id,
                    session_id,
                    reason,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    str(reporter_id),
                    str(reported_user_id),
                    session_id,
                    reason,
                    datetime.now(timezone.utc),
                ),
            )

        conn.commit()

        logger.info(
            "REPORT FILED | reporter=%s reported=%s session=%s reason=%s",
            reporter_id,
            reported_user_id,
            session_id,
            reason,
        )

    except Exception:
        logger.exception(
            "REPORT FAILED | reporter=%s reported=%s session=%s",
            reporter_id,
            reported_user_id,
            session_id,
        )
    finally:
        conn.close()
