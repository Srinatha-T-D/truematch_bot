# bot/handlers/next.py

from telegram import Update
from telegram.ext import ContextTypes

# Re-export the real /next logic
from bot.handlers.match import next_command as _next_command


async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /next command.
    Properly ends current chat (if any) and finds a new match.
    """
    await _next_command(update, context)
