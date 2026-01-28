# bot/handlers/vip_features/reconnect.py
# VIP Reconnect UI handler (presentation layer only)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.vip_features.reconnect import VipReconnectService
from bot.handlers.match import match_command


async def show_reconnect_ui(query, context: ContextTypes.DEFAULT_TYPE):
    """
    Show recent anonymous connections for VIP reconnect.
    """
    user_id = query.from_user.id

    partners = VipReconnectService.get_recent_partners(user_id)

    if not partners:
        await query.edit_message_text(
            "❌ No recent connections available for reconnect."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"🔁 Reconnect #{i + 1}",
                callback_data=f"vip_reconnect:{partner_id}",
            )
        ]
        for i, partner_id in enumerate(partners)
    ]

    await query.edit_message_text(
        "🔁 *Reconnect with a previous match:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def reconnect_callback(update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle reconnect selection.
    """
    query = update.callback_query
    await query.answer()

    # partner_id is stored for matchmaking layer (if needed later)
    partner_id = query.data.split(":", 1)[1]
    context.user_data["reconnect_partner"] = partner_id

    await query.edit_message_text(
        "⏳ Attempting reconnect..."
    )

    # Reuse normal matching flow
    await match_command(update, context)
