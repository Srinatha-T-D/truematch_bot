# bot/app.py
# FINAL application wiring — aligned with frozen core logic

import logging

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from bot.config.settings import BOT_TOKEN

# ---------------- CORE ----------------
from bot.handlers.start import start_handler, registration_callback
from bot.handlers.match import match_command
from bot.handlers.next import next_command
from bot.handlers.chat import chat_message
from bot.handlers.disconnect import disconnect_callback
from bot.handlers.consent import consent_callback
from bot.handlers.reset_profile import reset_profile_command
from bot.handlers.vip_callbacks import vip_callback_router
from bot.handlers.vip_features.preferences_ui import vip_preferences_callback
from bot.handlers.verify import verify_command
from bot.handlers.verify_steps import (
    verify_text_handler,
    verify_gender_callback,
)

# ---------------- USER / PROFILE ----------------
from bot.handlers.profile import profile_callback

# ---------------- VIP SERVICES ----------------
from bot.handlers.vipservices import vipservices
from bot.handlers.vip_filters import (
    vip_filters_menu,
    vip_age_menu,
    vip_age_callback,
    vip_state_menu,
    vip_state_callback,
    vip_language_menu,
    vip_language_callback,
    vip_verified_only,
    vip_reset_filters,
)

# ---------------- PAYMENTS ----------------
from bot.handlers.payments import (
    send_vip_menu,
    vip_tier_callback,
    send_vip_invoice,
    precheckout_handler,
    successful_payment_handler,
)

# ---------------- ADMIN ----------------
from bot.handlers.admin import grantvip_command
from bot.handlers.admin_verification import (
    verify_pending,
    verify_approve,
    verify_reject,
    verify_stats,   # ✅ FIXED IMPORT
)

# ---------------- ERROR ----------------
from bot.handlers.error import error_handler

logger = logging.getLogger(__name__)


# ======================================================
# APPLICATION SETUP (CLEAN & FINAL)
# ======================================================
def create_application() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()

    # ---------------- COMMANDS ----------------
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("find", match_command))
    app.add_handler(CommandHandler("next", next_command))
    app.add_handler(CommandHandler("vip", send_vip_menu))
    app.add_handler(CommandHandler("vipservices", vipservices))
    app.add_handler(CommandHandler("grantvip", grantvip_command))
    app.add_handler(CommandHandler("reset_profile", reset_profile_command))
    app.add_handler(CommandHandler("verify", verify_command))

    # 🔐 VERIFICATION (ADMIN)
    app.add_handler(CommandHandler("verify_pending", verify_pending))
    app.add_handler(CommandHandler("verify_approve", verify_approve))
    app.add_handler(CommandHandler("verify_reject", verify_reject))
    app.add_handler(CommandHandler("verify_stats", verify_stats))  # ✅ now works

    # ---------------- REGISTRATION ----------------
    app.add_handler(
        CallbackQueryHandler(registration_callback, pattern="^reg_")
    )

    # ---------------- VERIFICATION FLOW ----------------
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, verify_text_handler)
    )
    app.add_handler(
        CallbackQueryHandler(verify_gender_callback, pattern="^verify_gender:")
    )

    # ---------------- START MATCHING (BUTTON) ----------------
    app.add_handler(
        CallbackQueryHandler(match_command, pattern="^start_matching$")
    )

    # ---------------- CORE CALLBACKS ----------------
    app.add_handler(
        CallbackQueryHandler(consent_callback, pattern="^consent_")
    )
    app.add_handler(
        CallbackQueryHandler(profile_callback, pattern="^(gender:|looking:)")
    )
    app.add_handler(
        CallbackQueryHandler(disconnect_callback, pattern="^chat:disconnect$")
    )

    # ---------------- VIP CALLBACK ROUTER ----------------
    app.add_handler(
        CallbackQueryHandler(vip_callback_router, pattern="^vip_")
    )
    app.add_handler(
        CallbackQueryHandler(vip_preferences_callback, pattern="^vip_pref:")
    )

    # ---------------- VIP FILTER FLOW ----------------
    app.add_handler(CallbackQueryHandler(vip_filters_menu, pattern="^vip_filters$"))
    app.add_handler(CallbackQueryHandler(vip_age_menu, pattern="^vip_age_menu$"))
    app.add_handler(CallbackQueryHandler(vip_age_callback, pattern="^vip_age:"))
    app.add_handler(CallbackQueryHandler(vip_state_menu, pattern="^vip_state_menu$"))
    app.add_handler(CallbackQueryHandler(vip_state_callback, pattern="^vip_state:"))
    app.add_handler(
        CallbackQueryHandler(vip_language_menu, pattern="^vip_language_menu$")
    )
    app.add_handler(
        CallbackQueryHandler(vip_language_callback, pattern="^vip_lang:")
    )
    app.add_handler(
        CallbackQueryHandler(vip_verified_only, pattern="^vip_verified_only$")
    )
    app.add_handler(
        CallbackQueryHandler(vip_reset_filters, pattern="^vip_reset_filters$")
    )

    # ---------------- PAYMENTS ----------------
    app.add_handler(
        CallbackQueryHandler(vip_tier_callback, pattern="^vip:tier:")
    )
    app.add_handler(
        CallbackQueryHandler(send_vip_invoice, pattern="^vip:buy:")
    )
    app.add_handler(
        CallbackQueryHandler(send_vip_menu, pattern="^vip:buy$")
    )
    app.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    app.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler)
    )

    # ---------------- CHAT ----------------
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message)
    )

    # ---------------- ERROR ----------------
    app.add_error_handler(error_handler)

    logger.info("✅ TrueMatch application started (clean core)")

    return app

