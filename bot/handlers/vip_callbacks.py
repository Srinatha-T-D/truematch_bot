# bot/handlers/vip_callbacks.py
# Central router for all VIP inline callbacks

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.access_control import AccessControlService
from bot.core.users import is_vip_user
from bot.utils.logger import logger
from bot.services.vip_features.preferences import VipPreferencesService

from bot.handlers.vip_features.filters_ui import show_filters_ui
from bot.handlers.vip_features.preferences_ui import show_preferences_ui
from bot.handlers.vip_features.insights_ui import show_insights_ui
from bot.handlers.vip_features.verification_ui import show_verification_ui
from bot.handlers.vip_features.reconnect import (
    show_reconnect_ui,
    reconnect_callback,
)


async def vip_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    user_id = query.from_user.id
    data = query.data or ""

    # --------------------------
    # 🔐 VIP ACCESS GATE
    # --------------------------
    try:
        has_access = await AccessControlService.can_access_vip_features(user_id)
    except Exception:
        has_access = is_vip_user(user_id)

    if not has_access:
        try:
            await query.edit_message_text(
                "⭐ VIP access required to use this feature."
            )
        except Exception:
            pass
        return

    logger.info("[VIP CALLBACK] user=%s action=%s", user_id, data)

    # --------------------------
    # ⭐ VIP PREFERENCES (SAVE)
    # --------------------------
    if data.startswith("vip_pref:"):
        updates = {}

        if data == "vip_pref:same_language":
            updates["prefer_same_language"] = True
            label = "Same language"

        elif data == "vip_pref:verified":
            updates["prefer_verified_users"] = True
            label = "Verified users"

        elif data == "vip_pref:vip":
            updates["prefer_vip_users"] = True
            label = "VIP users"

        else:
            return

        VipPreferencesService.save_preferences(user_id, **updates)

        logger.info("[VIP PREF] user=%s updated=%s", user_id, updates)

        await query.message.reply_text(
            f"✅ *Preference saved*\n\n"
            f"Matches will now prefer: *{label}*.",
            parse_mode="Markdown",
        )
        return

    # --------------------------
    # 🎛 ROUTING
    # --------------------------
    if data == "vip_filters":
        await show_filters_ui(query, context)

    elif data == "vip_preferences":
        await show_preferences_ui(query, context)

    elif data == "vip_insights":
        await show_insights_ui(query, context)

    elif data == "vip_verification":
        await show_verification_ui(query, context)

    elif data == "vip_reconnect":
        await show_reconnect_ui(query, context)

    elif data.startswith("vip_reconnect:"):
        await reconnect_callback(update, context)

    else:
        logger.warning(
            "[VIP CALLBACK] Unknown action user=%s data=%s",
            user_id,
            data,
        )
        try:
            await query.edit_message_text("Unknown VIP action.")
        except Exception:
            pass
