# bot/core/timeout.py
# Inactivity auto-timeout watcher for active chats

import time
import logging
import asyncio
from typing import Dict

from bot.core.matchmaking import ACTIVE_CHATS, disconnect_users

logger = logging.getLogger(__name__)

# ⏳ Inactivity timeout (seconds)
TIMEOUT_SECONDS = 300

# user_id -> last_activity_timestamp
LAST_ACTIVITY: Dict[int, float] = {}


# =========================
# ACTIVITY TRACKING
# =========================

def mark_activity(user_id: int):
    """
    Mark user as active (called on every message).
    """
    LAST_ACTIVITY[int(user_id)] = time.time()


# =========================
# TIMEOUT WATCHER
# =========================

async def timeout_watcher(bot):
    """
    Background task that disconnects inactive chats safely.
    Runs forever.
    """
    logger.info("⏳ Inactivity timeout watcher started")

    while True:
        await asyncio.sleep(30)

        now = time.time()
        processed = set()

        # Snapshot to avoid runtime mutation issues
        active_snapshot = list(ACTIVE_CHATS.items())

        for user_id, chat in active_snapshot:
            if user_id in processed:
                continue

            try:
                partner_id, partner_chat_id, _ = chat
            except ValueError:
                # Corrupted entry – skip safely
                continue

            user_id = int(user_id)
            partner_id = int(partner_id)

            last_user = LAST_ACTIVITY.get(user_id, now)
            last_partner = LAST_ACTIVITY.get(partner_id, now)

            last_active = max(last_user, last_partner)

            if now - last_active < TIMEOUT_SECONDS:
                continue

            logger.info(
                "⏳ Auto-timeout disconnect: %s <-> %s",
                user_id,
                partner_id,
            )

            # 🔐 End session (safe if already disconnected)
            disconnect_users(user_id)

            # 🔔 Notify users (best-effort)
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text="⏳ Chat ended due to inactivity.",
                )
                await bot.send_message(
                    chat_id=partner_chat_id,
                    text="⏳ Chat ended due to inactivity.",
                )
            except Exception:
                pass

            # 🧹 Cleanup activity state
            LAST_ACTIVITY.pop(user_id, None)
            LAST_ACTIVITY.pop(partner_id, None)

            processed.add(user_id)
            processed.add(partner_id)
