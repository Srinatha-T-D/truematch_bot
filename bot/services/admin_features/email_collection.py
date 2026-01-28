import re
from bot.core.db import get_db
from bot.utils.logger import logger


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailCollectionService:

    @staticmethod
    def is_valid_email(email: str) -> bool:
        return bool(EMAIL_REGEX.match(email))

    @staticmethod
    async def save_email(user_id: int, email: str) -> bool:
        if not EmailCollectionService.is_valid_email(email):
            return False

        query = """
            UPDATE users
            SET email = $1,
                email_opt_in = TRUE,
                email_verified = FALSE
            WHERE telegram_id = $2
        """
        async with get_db() as conn:
            await conn.execute(query, email.lower(), user_id)

        logger.info(f"[EMAIL] Collected email for user {user_id}")
        return True

    @staticmethod
    async def opt_out(user_id: int):
        query = """
            UPDATE users
            SET email_opt_in = FALSE
            WHERE telegram_id = $1
        """
        async with get_db() as conn:
            await conn.execute(query, user_id)

        logger.info(f"[EMAIL] User {user_id} opted out")
