from bot.core.ban import ban_user
from bot.core import db

REPORT_LIMIT = 3

def report_user(user_id: int) -> bool:
    count = db.increment_report(user_id)
    if count >= REPORT_LIMIT:
        ban_user(user_id)
        return True
    return False
