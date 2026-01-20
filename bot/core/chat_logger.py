# bot/core/chat_logger.py

import uuid
from datetime import datetime, timedelta
from bot.core.database import execute

RETENTION_DAYS = 14


async def create_chat_session(user_a: int, user_b: int) -> str:
    session_id = str(uuid.uuid4())

    await execute(
        """
        INSERT INTO chat_sessions (id, user_a, user_b, started_at)
        VALUES ($1, $2, $3, $4)
        """,
        session_id,
        user_a,
        user_b,
        datetime.utcnow(),
    )

    return session_id


async def end_chat_session(session_id: str):
    await execute(
        """
        UPDATE chat_sessions
        SET ended_at = $2
        WHERE id = $1
        """,
        session_id,
        datetime.utcnow(),
    )


async def log_message(session_id: str, sender_id: int, message: str):
    await execute(
        """
        INSERT INTO chat_messages (session_id, sender_id, message, sent_at)
        VALUES ($1, $2, $3, $4)
        """,
        session_id,
        sender_id,
        message,
        datetime.utcnow(),
    )


async def cleanup_old_chats():
    cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)

    await execute(
        "DELETE FROM chat_sessions WHERE started_at < $1",
        cutoff,
    )
