from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def show_filters_ui(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎂 Age Filter", callback_data="filter_age")],
        [InlineKeyboardButton("📍 State Filter", callback_data="filter_state")],
        [InlineKeyboardButton("🗣️ Language Filter", callback_data="filter_language")],
    ]

    await query.edit_message_text(
        "🎯 *VIP Match Filters*\n\n"
        "Choose a filter to configure:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
