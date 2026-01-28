from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.access_control import AccessControlService
from bot.utils.logger import logger
from bot.handlers.match import match_command


# =========================
# VIP SERVICES DASHBOARD
# =========================
async def vipservices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    can_access = await AccessControlService.can_access_vip_features(user_id)
    access_snapshot = await AccessControlService.get_access_snapshot(user_id)

    logger.info(f"[VIP SERVICES] user={user_id} snapshot={access_snapshot}")

    if not can_access:
        await update.message.reply_text(
            "⭐ *VIP Services*\n\n"
            "These features are available only for VIP members.\n\n"
            "👉 Upgrade to VIP to unlock these features.",
            parse_mode="Markdown",
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("🎯 Match Filters", callback_data="vip_filters"),
            InlineKeyboardButton("⚙️ Preferences", callback_data="vip_preferences"),
        ],
        [
            InlineKeyboardButton("🔁 Reconnect", callback_data="vip_reconnect"),
            InlineKeyboardButton("📊 Insights", callback_data="vip_insights"),
        ],
        [
            InlineKeyboardButton("🔒 Verification", callback_data="vip_verification"),
        ],
    ]

    await update.message.reply_text(
        "🎉 *VIP Services*\n\nChoose a service below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# VIP PREFERENCES
# =========================
async def vip_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🗣 Prefer Same Language", callback_data="pref_language")],
        [InlineKeyboardButton("🔒 Prefer Verified Users", callback_data="pref_verified")],
        [InlineKeyboardButton("⭐ Prefer VIP Users", callback_data="pref_vip")],
    ]

    await query.message.reply_text(
        "⚙️ *VIP Preferences*\n\nThese preferences influence match ranking:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# VIP FILTERS (PLACEHOLDER)
# =========================
async def vip_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🎯 *Match Filters*\n\nFilter settings will be available here.",
        parse_mode="Markdown",
    )


# =========================
# VIP RECONNECT
# =========================
async def vip_reconnect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "❌ No recent connections available for reconnect.",
        parse_mode="Markdown",
    )


# =========================
# VIP INSIGHTS
# =========================
async def vip_insights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📊 *VIP Insights*\n\nInsights will appear after more activity.",
        parse_mode="Markdown",
    )


# =========================
# VIP VERIFICATION
# =========================
async def vip_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔒 *Verification*\n\nVerification features coming soon.",
        parse_mode="Markdown",
    )


# =========================
# START MATCHING BUTTON
# =========================
async def start_matching_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Start Matching", callback_data="vip_start_match")]
    ]

    await update.message.reply_text(
        "🎉 *All preferences saved successfully!*\n\n"
        "You can now start matching.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# START MATCHING CALLBACK
# =========================
async def vip_start_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.message.edit_reply_markup(None)
    except Exception:
        pass

    if context.user_data.get("intent"):
        await match_command(update, context)
        return

    keyboard = [
        [
            InlineKeyboardButton("👨 Looking for Female", callback_data="vip_intent:female"),
            InlineKeyboardButton("👩 Looking for Male", callback_data="vip_intent:male"),
        ],
        [
            InlineKeyboardButton("🌈 Any", callback_data="vip_intent:any"),
        ],
    ]

    await query.message.reply_text(
        "🔍 *Who are you looking for?*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# SAVE INTENT + AUTO MATCH
# =========================
async def vip_intent_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    intent = query.data.split(":", 1)[1]
    context.user_data["intent"] = intent

    try:
        await query.message.edit_reply_markup(None)
    except Exception:
        pass

    await query.message.reply_text(
        "✅ Preference saved.\n\n⏳ Connecting you now…"
    )

    await match_command(update, context)
