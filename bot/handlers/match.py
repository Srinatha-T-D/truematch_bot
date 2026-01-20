# bot/handlers/match.py

import logging
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.matchmaking import add_to_queue, get_partner, disconnect_users
from bot.core.trials import can_user_chat
from bot.core.cooldown import is_on_cooldown, set_cooldown
from bot.config.settings import GLOBAL_FREE_START, GLOBAL_FREE_END
from bot.utils.keyboards import vip_keyboard

logger = logging.getLogger(__name__)


async def match_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enqueue_for_match(update, context)


async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    partner = get_partner(user.id)
    if partner:
        disconnect_users(user.id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔁 Finding a new partner...",
        )

    await enqueue_for_match(update, context)


async def enqueue_for_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # ==========================
    # ⏱ COOLDOWN CHECK
    # ==========================
    remaining = await is_on_cooldown(user.id)
    if remaining > 0:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ Please wait {remaining}s before trying again.",
        )
        return

    intent = context.user_data.get("intent")
    if not intent:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❗ Please choose what you are looking for using /start",
        )
        return

    today = date.today()
    is_global_free = GLOBAL_FREE_START <= today <= GLOBAL_FREE_END

    # 🔥 GLOBAL FREE = ALWAYS ALLOW
    if not is_global_free:
        allowed = await can_user_chat(user.id)
        if not allowed:
            await context.bot.send_message(
                chat_id=chat_id,
                text="🚫 *Access limit reached*\n\nUpgrade to VIP to continue chatting.",
                reply_markup=vip_keyboard(),
                parse_mode="Markdown",
            )
            return

    # ==========================
    # ✅ UX POLISH (NEW)
    # ==========================
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "⏳ *Connecting you to someone…*\n\n"
            "You’ll be matched anonymously.\n"
            "Please wait."
        ),
        parse_mode="Markdown",
    )

    # ✅ Set cooldown only when enqueue is valid
    await set_cooldown(user.id)

    await add_to_queue(
        user_id=user.id,
        chat_id=chat_id,
        intent=intent,
        context=context,
    )

    logger.info(
        f"User {user.id} queued (intent={intent}, global_free={is_global_free})"
    )
