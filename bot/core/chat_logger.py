# bot/core/chat_logger.py
# Chat session lifecycle + privacy-safe analytics
# Single source of truth for session start/end

import uuid
import logging
from datetime import datetime, timedelta, timezone

from bot.core.db import get_db
from bot.services.vip_features.session_logger import VipSessionLogger
from bot.services.vip_features.reconnect import VipReconnectService

logger = logging.getLogger(__name__)

RETENTION_DAYS = 14


# =========================
# CHAT SESSION MANAGEMENT
# =========================

async def create_chat_session(user_a: int, user_b: int) -> str:
    """
    Create a new chat session and return session_id (UUID).
    """
    user_a = int(user_a)
    user_b = int(user_b)

    session_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_sessions (id, user_a, user_b, started_at)
                VALUES (%s, %s, %s, %s)
                """,
                (session_id, user_a, user_b, started_at),
            )
        conn.commit()

        logger.info(
            "✅ CHAT SESSION CREATED | session=%s users=%s,%s",
            session_id,
            user_a,
            user_b,
        )
        return session_id

    except Exception:
        logger.exception(
            "💥 FAILED TO CREATE CHAT SESSION | users=%s,%s",
            user_a,
            user_b,
        )
        raise
    finally:
        conn.close()


async def end_chat_session(session_id: str) -> None:
    """
    Mark chat session as ended and log analytics + reconnect history.
    This function must NEVER raise.
    """
    logger.info("🔥 end_chat_session START | session=%s", session_id)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Fetch active session
            cur.execute(
                """
                SELECT user_a, user_b, started_at
                FROM chat_sessions
                WHERE id = %s AND ended_at IS NULL
                """,
                (session_id,),
            )
            row = cur.fetchone()

            if not row:
                logger.warning(
                    "⚠️ No active chat session found | session=%s",
                    session_id,
                )
                return

            user_a, user_b, started_at = row
            ended_at = datetime.now(timezone.utc)

            # Mark session ended
            cur.execute(
                """
                UPDATE chat_sessions
                SET ended_at = %s
                WHERE id = %s
                """,
                (ended_at, session_id),
            )

        conn.commit()

    except Exception:
        logger.exception(
            "💥 Failed to update chat_sessions | session=%s",
            session_id,
        )
        return
    finally:
        conn.close()

    # ---- Analytics (best-effort, never block) ----
    try:
        VipSessionLogger.log_session(
            user_id=int(user_a),
            partner_id=int(user_b),
            started_at=started_at,
            ended_at=ended_at,
        )
        VipSessionLogger.log_session(
            user_id=int(user_b),
            partner_id=int(user_a),
            started_at=started_at,
            ended_at=ended_at,
        )
    except Exception:
        logger.exception(
            "⚠️ Analytics logging failed | session=%s",
            session_id,
        )

    # ---- VIP Reconnect history (best-effort, never block) ----
    try:
        VipReconnectService.save_connection(
            str(user_a),
            str(user_b),
        )
    except Exception:
        logger.exception(
            "⚠️ VIP reconnect history save failed | session=%s",
            session_id,
        )

    logger.info(
        "✅ CHAT SESSION ENDED | users=%s,%s duration=%ss",
        user_a,
        user_b,
        int((ended_at - started_at).total_seconds()),
    )


# =========================
# MESSAGE LOGGING (STUB)
# =========================

def log_message(*_args, **_kwargs) -> None:
    """
    Message logging disabled.
    Kept as stub to prevent handler crashes.
    """
    return


# =========================
# CLEANUP
# =========================

def cleanup_old_chats() -> None:
    """
    Delete fully ended sessions older than retention window.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM chat_sessions
                WHERE ended_at IS NOT NULL
                  AND ended_at < %s
                """,
                (cutoff,),
            )
        conn.commit()
    finally:
        conn.close()
