# bot/handlers/start.py
# Entry point — enforces registration before any matching
# FINAL FIXED VERSION

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.core.users import (
    get_or_create_user,
    get_user_by_id,
    update_user_preferences,
)
from bot.core.referral import apply_referral


# =========================
# /start HANDLER
# =========================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = user.username

    # Ensure user exists
    get_or_create_user(user_id, username)

    # ------------------------------------------
    # Referral handling
    # ------------------------------------------
    args = context.args or []
    if args:
        referrer_id = args[0]
        if referrer_id != user_id:
            await apply_referral(user_id, referrer_id)

    # ------------------------------------------
    # Registration check
    # ------------------------------------------
    user_row = get_user_by_id(user_id)

    if not user_row.get("gender") or not user_row.get("looking_for"):
        await _ask_gender(update, context)
        context.user_data["reg_step"] = "gender"
        return

    # ------------------------------------------
    # Already registered → main menu
    # ------------------------------------------
    await _show_main_menu(update, context)


# =========================
# REGISTRATION STEPS
# =========================
async def _ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👨 Male", callback_data="reg_gender:male"),
            InlineKeyboardButton("👩 Female", callback_data="reg_gender:female"),
        ]
    ]

    if update.message:
        await update.message.reply_text(
            "👋 *Welcome to TrueMatch!*\n\n"
            "Let’s get started.\n\n"
            "*Select your gender:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    else:
        await update.callback_query.message.edit_text(
            "*Select your gender:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )


async def _ask_looking_for(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👨 Men", callback_data="reg_looking:male"),
            InlineKeyboardButton("👩 Women", callback_data="reg_looking:female"),
        ]
    ]

    await update.callback_query.message.edit_text(
        "*Who are you looking to chat with?*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# REGISTRATION CALLBACK
# =========================
async def registration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data

    # --------------------------
    # Gender
    # --------------------------
    if data.startswith("reg_gender:"):
        gender = data.split(":", 1)[1]
        update_user_preferences(user_id, gender=gender)

        context.user_data["reg_step"] = "looking_for"
        await _ask_looking_for(update, context)
        return

    # --------------------------
    # Looking for
    # --------------------------
    if data.startswith("reg_looking:"):
        looking_for = data.split(":", 1)[1]
        update_user_preferences(user_id, looking_for=looking_for)

        context.user_data.pop("reg_step", None)

        await query.message.edit_text(
            "✅ *Registration completed successfully!*",
            parse_mode="Markdown",
        )

        await _show_main_menu(update, context)
        return


# =========================
# MAIN MENU (SAFE FOR MESSAGE + CALLBACK)
# =========================
async def _show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Find Anonymous Chat", callback_data="start_matching")],
        [InlineKeyboardButton("⭐ Buy VIP", callback_data="vip:buy")],
    ]

    text = (
        "🎉 *Welcome to TrueMatch!*\n\n"
        "🔐 Anonymous 1-to-1 chats\n"
        "🚫 No spam or abuse\n"
        "⭐ VIP unlocks unlimited chats\n\n"
        "👇 Choose an option below"
    )

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    else:
        await update.callback_query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

