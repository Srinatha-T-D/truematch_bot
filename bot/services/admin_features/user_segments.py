from bot.core.db import get_db


class UserSegmentService:

    @staticmethod
    async def free_users():
        query = """
            SELECT telegram_id FROM users
            WHERE vip_until IS NULL
              AND email_opt_in = TRUE
        """
        async with get_db() as conn:
            rows = await conn.fetch(query)
        return [r["telegram_id"] for r in rows]

    @staticmethod
    async def inactive_users(days: int = 30):
        query = """
            SELECT telegram_id FROM users
            WHERE last_active < NOW() - INTERVAL '%s days'
              AND email_opt_in = TRUE
        """ % days

        async with get_db() as conn:
            rows = await conn.fetch(query)
        return [r["telegram_id"] for r in rows]

    @staticmethod
    async def vip_users():
        query = """
            SELECT telegram_id FROM users
            WHERE vip_until >= NOW()
              AND email_opt_in = TRUE
        """
        async with get_db() as conn:
            rows = await conn.fetch(query)
        return [r["telegram_id"] for r in rows]
