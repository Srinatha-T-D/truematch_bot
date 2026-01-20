from bot.core import db, redis

def ban_user(user_id: int):
    db.set_banned(user_id, True)
    redis.remove_from_queue(user_id)
    redis.end_chat(user_id)
