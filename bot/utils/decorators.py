from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.admin import is_admin

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            await update.message.reply_text("❌ Admin only")
            return
        return await func(update, context)
    return wrapper
