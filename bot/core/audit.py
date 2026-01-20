# bot/core/audit.py

import json
import logging
from bot.core.database import execute

logger = logging.getLogger(__name__)


async def log_admin_action(
    admin_id: int,
    action: str,
    metadata: dict | None = None,
):
    """
    Store admin actions for auditing purposes.
    """
    try:
        await execute(
            """
            INSERT INTO admin_audit (admin_id, action, metadata)
            VALUES ($1, $2, $3)
            """,
            admin_id,
            action,
            json.dumps(metadata or {}),
        )
    except Exception:
        logger.exception("Failed to log admin action")
