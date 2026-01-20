# bot/core/reporting.py

from datetime import datetime
from bot.core.database import execute


async def file_report(
    session_id: str,
    reporter_id: int,
    reason: str,
):
    await execute(
        """
        INSERT INTO chat_reports (session_id, reporter_id, reason, reported_at)
        VALUES ($1, $2, $3, $4)
        """,
        session_id,
        reporter_id,
        reason,
        datetime.utcnow(),
    )
