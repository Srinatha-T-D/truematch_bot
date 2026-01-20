# bot/app.py

import logging
import asyncio

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from bot.config.settings import BOT_TOKEN
from bot.core.timeout import timeout_watcher

# ---------------- HANDLERS ----------------

# User handlers
from bot.handlers.start import start_handler
from bot.handlers.intent import intent_callback
from bot.handlers.profile import profile_callback
from bot.handlers.match import match_command, next_command
from bot.handlers.chat import chat_message
from bot.handlers.disconnect import disconnect_callback
from bot.handlers.vipstatus import vipstatus_command
from bot.handlers.next import next_command
from bot.handlers.rules import rules_command
from bot.handlers.invite import invite_command
from bot.handlers.refstats import refstats_command
from bot.handlers.invites import invites_command
from bot.handlers.stop import stop_command
from bot.handlers.help import help_handler
from bot.handlers.admin_revenue import revenue_handler
from bot.handlers.admin_systemhealth import systemhealth_handler
from bot.handlers.admin_help import adminhelp_handler
from bot.handlers.admin_readchat import readchat_handler
from bot.handlers.error import error_handler
from bot.handlers.admin_ban import ban_handler, unban_handler
from bot.handlers.admin_alerts import alerts_handler
from bot.handlers.admin_history import chat_history_command, view_chat_command
from bot.handlers.admin_audit import (
    active_chats_command,
    force_stop_command,
)
from bot.handlers.report import (
    report_entry_callback,
    report_reason_callback,
)

# Payments
from bot.handlers.payments import (
    send_vip_menu,
    vip_tier_callback,
    send_vip_invoice,
    precheckout_handler,
    successful_payment_handler,
)

# Admin
from bot.handlers.admin import (
    stats_command,
    users_command,
    grantvip_command,
)

logger = logging.getLogger(__name__)


# 🔹 This runs AFTER event loop starts
async def post_init(application: Application):
    from bot.core.recovery import crash_recovery
    from bot.core.timeout import timeout_watcher
    import asyncio
    from bot.core.chat_logger import cleanup_old_chats
    await cleanup_old_chats()

    # 🧯 Crash recovery first
    await crash_recovery()

    # ⏳ Start auto-timeout watcher
    asyncio.create_task(timeout_watcher(application.bot))

    logger.info("🧯 Crash recovery done, ⏳ auto-timeout watcher started")


def create_application() -> Application:
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)  # ✅ correct place
        .build()
    )

    # ---------------- COMMANDS ----------------
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("find", match_command))
    application.add_handler(CommandHandler("next", next_command))
    application.add_handler(CommandHandler("vip", send_vip_menu))
    application.add_handler(CommandHandler("vipstatus", vipstatus_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("grantvip", grantvip_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("activechats", active_chats_command))
    application.add_handler(CommandHandler("force_stop", force_stop_command))
    application.add_handler(CommandHandler("chat_history", chat_history_command))
    application.add_handler(CommandHandler("view_chat", view_chat_command))
    application.add_handler(CommandHandler("invite", invite_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("next", next_command))
    application.add_handler(CommandHandler("invites", invites_command))
    application.add_handler(CommandHandler("refstats", refstats_command))
    application.add_error_handler(error_handler)
    application.add_handler(readchat_handler)
    application.add_handler(revenue_handler)
    application.add_handler(systemhealth_handler)
    application.add_handler(help_handler)
    application.add_handler(adminhelp_handler)
    application.add_handler(alerts_handler)
    application.add_handler(ban_handler)
    application.add_handler(unban_handler)

    # ---------------- CALLBACKS ----------------
    application.add_handler(
        CallbackQueryHandler(intent_callback, pattern="^intent:")
    )
    application.add_handler(
        CallbackQueryHandler(profile_callback, pattern="^(gender:|looking:)")
    )
    application.add_handler(
        CallbackQueryHandler(vip_tier_callback, pattern="^vip:tier:")
    )
    application.add_handler(
        CallbackQueryHandler(send_vip_invoice, pattern="^vip:buy:")
    )
    application.add_handler(
        CallbackQueryHandler(disconnect_callback, pattern="^chat:disconnect$")
    )
    application.add_handler(
        CallbackQueryHandler(report_entry_callback, pattern="^chat:report$")
    )
    application.add_handler(
        CallbackQueryHandler(report_reason_callback, pattern="^report:")
    )

    # ---------------- PAYMENTS ----------------
    application.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler)
    )

    # ---------------- CHAT ----------------
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message)
    )

    logger.info("✅ Telegram application created and handlers registered")
    return application
