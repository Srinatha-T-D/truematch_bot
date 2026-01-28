from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services.vip_features.preferences import VipPreferencesService
from bot.utils.logger import logger


# =========================
# SHOW PREFERENCES UI
# =========================
async def show_preferences_ui(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🗣️ Prefer Same Language",
                callback_data="vip_pref:same_language",
            )
        ],
        [
            InlineKeyboardButton(
                "🔒 Prefer Verified Users",
                callback_data="vip_pref:verified",
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ Prefer VIP Users",
                callback_data="vip_pref:vip",
            )
        ],
    ]

    await query.edit_message_text(
        "⚙️ *VIP Preferences*\n\n"
        "These preferences influence match ranking.\n"
        "Tap to toggle:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# HANDLE PREFERENCE TOGGLE
# =========================
async def vip_preferences_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

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

    logger.info(
        "[VIP PREF UI] user=%s updated=%s", user_id, updates
    )

    await query.message.reply_text(
        f"✅ *Preference saved*\n\n"
        f"Matches will now prefer: *{label}*.",
        parse_mode="Markdown",
    )
