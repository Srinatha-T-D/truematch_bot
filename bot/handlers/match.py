# bot/handlers/match.py
# Handles /find and /next — orchestration only (logic-free)

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import try_match, get_partner, disconnect_users
from bot.core.trials import can_user_chat
from bot.core.cooldown import is_on_cooldown, set_cooldown
from bot.utils.keyboards import vip_keyboard, consent_keyboard
from bot.utils.states import CONSENT_WAIT

logger = logging.getLogger(__name__)


# =========================
# /find
# =========================
async def match_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_find(update, context)


# =========================
# /next
# =========================
async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    partner = get_partner(user.id)
    if partner:
        partner_id, partner_chat_id, _ = partner
        disconnect_users(user.id)

        await context.bot.send_message(
            chat_id=chat_id,
            text="🔁 Skipping… finding a new partner.",
        )

        try:
            await context.bot.send_message(
                chat_id=partner_chat_id,
                text="❌ Your partner has left the chat.",
            )
        except Exception:
            pass

    await _handle_find(update, context)


# =========================
# CORE /find FLOW
# =========================
async def _handle_find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # ⏱ Cooldown
    remaining = await is_on_cooldown(user.id)
    if remaining > 0:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ Please wait {remaining}s before trying again.",
        )
        return

    # 🔐 Trial / VIP access
    if not can_user_chat(user.id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="🚫 *Access limit reached*\n\nUpgrade to VIP to continue chatting.",
            reply_markup=vip_keyboard(),
            parse_mode="Markdown",
        )
        return

    # UX feedback
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "⏳ *Connecting you to someone…*\n\n"
            "You’ll be matched anonymously.\n"
            "Please wait."
        ),
        parse_mode="Markdown",
    )

    # set cooldown
    await set_cooldown(user.id)

    # 🚀 TRY MATCH (VIP or FREE decided internally)
    matched = await try_match(user.id, chat_id)

    if matched:
        logger.info("User %s matched immediately", user.id)
        return

    # ❗ CONSENT REQUIRED
    context.user_data["state"] = CONSENT_WAIT

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "❌ No users available for your preference right now.\n\n"
            "Would you like to connect with others?"
        ),
        reply_markup=consent_keyboard(),
    )

    logger.info("User %s awaiting consent", user.id)
