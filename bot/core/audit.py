# bot/core/audit.py

import json
import logging
from datetime import datetime, timezone

from bot.core.db import get_db

logger = logging.getLogger(__name__)


async def log_admin_action(
    admin_id: int,
    action: str,
    metadata: dict | None = None,
):
    """
    Store admin actions for auditing purposes.
    psycopg2-based (sync DB).
    """

    admin_id = str(admin_id)
    metadata_json = json.dumps(metadata or {})
    created_at = datetime.now(timezone.utc)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO admin_audit (admin_id, action, metadata, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    admin_id,
                    action,
                    metadata_json,
                    created_at,
                ),
            )
            conn.commit()

    except Exception:
        logger.exception("Failed to log admin action")

    finally:
        conn.close()
