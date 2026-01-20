# bot/core/timeout.py

import time
import logging
import asyncio

from bot.core.matchmaking import ACTIVE_CHATS, disconnect_users

logger = logging.getLogger(__name__)

# ⏳ 5 minutes inactivity
TIMEOUT_SECONDS = 300

# user_id -> last_activity_timestamp
LAST_ACTIVITY = {}


def mark_activity(user_id: int):
    LAST_ACTIVITY[user_id] = time.time()


async def timeout_watcher(bot):
    """
    Background task that disconnects inactive chats
    """
    while True:
        await asyncio.sleep(30)

        now = time.time()
        checked = set()

        for user_id, (partner_id, partner_chat_id, session_id) in list(ACTIVE_CHATS.items()):

            if user_id in checked:
                continue

            last_user = LAST_ACTIVITY.get(user_id, now)
            last_partner = LAST_ACTIVITY.get(partner_id, now)

            last_active = max(last_user, last_partner)

            if now - last_active >= TIMEOUT_SECONDS:
                logger.info(
                    f"Auto-timeout disconnect: {user_id} <-> {partner_id}"
                )

                disconnect_users(user_id)

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

                LAST_ACTIVITY.pop(user_id, None)
                LAST_ACTIVITY.pop(partner_id, None)

                checked.add(user_id)
                checked.add(partner_id)
