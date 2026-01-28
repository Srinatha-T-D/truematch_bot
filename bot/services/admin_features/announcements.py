from bot.core.db import get_db
from bot.utils.logger import logger


class AnnouncementService:

    @staticmethod
    async def log_email_event(user_id: int, event: str):
        query = """
            INSERT INTO email_events (user_id, event_type)
            VALUES ($1, $2)
        """
        async with get_db() as conn:
            await conn.execute(query, user_id, event)

        logger.info(f"[EMAIL EVENT] {event} → {user_id}")
