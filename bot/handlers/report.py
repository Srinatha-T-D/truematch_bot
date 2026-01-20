# bot/handlers/report.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.core.matchmaking import get_partner
from bot.core.reporting import file_report
from bot.config.settings import ADMIN_IDS


REPORT_REASONS = {
    "harassment": "Harassment",
    "spam": "Spam",
    "inappropriate": "Inappropriate content",
    "other": "Other",
}


async def report_entry_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    partner = get_partner(user.id)
    if not partner:
        await query.edit_message_text(
            "⚠️ No active or recent chat to report."
        )
        return

    _, _, session_id = partner

    context.user_data["report_session_id"] = session_id

    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"report:{k}")]
        for k, v in REPORT_REASONS.items()
    ]

    await query.edit_message_text(
        "🚩 *Report Chat*\n\nSelect a reason:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def report_reason_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data.split(":", 1)[1]

    session_id = context.user_data.get("report_session_id")
    if not session_id:
        await query.edit_message_text("⚠️ Report session expired.")
        return

    reason = REPORT_REASONS.get(data, "Other")

    await file_report(
        session_id=session_id,
        reporter_id=user.id,
        reason=reason,
    )

    # 🔔 Notify admins
    text = (
        "🚨 *New Chat Report*\n\n"
        f"Session: `{session_id}`\n"
        f"Reporter: `{user.id}`\n"
        f"Reason: *{reason}*\n\n"
        "Use /view_chat <session_id>"
    )

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode="Markdown",
            )
        except Exception:
            pass

    context.user_data.pop("report_session_id", None)

    await query.edit_message_text(
        "✅ Thanks for reporting.\nOur moderation team will review this chat."
    )
