from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.match import match_command  # this already exists

async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /next is an alias for /find
    """
    await match_command(update, context)
