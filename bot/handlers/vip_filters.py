from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.core.db import get_db


# =========================
# HELPER: DELETE CURRENT MENU
# =========================
async def delete_menu(query):
    try:
        await query.message.delete()
    except Exception:
        pass


# =========================
# DASHBOARD → FILTER START
# =========================
async def vip_filters_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    keyboard = [
        [InlineKeyboardButton("🎂 Age Filter", callback_data="vip_age_menu")],
        [InlineKeyboardButton("📍 State Filter", callback_data="vip_state_menu")],
        [InlineKeyboardButton("🗣 Language Filter", callback_data="vip_language_menu")],
        [InlineKeyboardButton("✅ Verified Users Only", callback_data="vip_verified_only")],
        [InlineKeyboardButton("🔄 Reset All Filters", callback_data="vip_reset_filters")],
    ]

    await query.message.chat.send_message(
        "🎯 *VIP Match Filters*\n\nSet your preferences. "
        "If no exact match is found, filters may relax but gender never changes.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# AGE FILTER
# =========================
async def vip_age_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    ranges = [(18, 25), (21, 30), (26, 35), (30, 40), (35, 50)]

    keyboard = [
        [InlineKeyboardButton(f"{a} – {b}", callback_data=f"vip_age:{a}:{b}")]
        for a, b in ranges
    ]

    await query.message.chat.send_message(
        "🎂 *Select Age Range*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def vip_age_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    user_id = str(query.from_user.id)
    _, age_min, age_max = query.data.split(":")

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET age_min=%s, age_max=%s WHERE user_id=%s",
            (int(age_min), int(age_max), user_id),
        )
        conn.commit()
    conn.close()

    await query.message.chat.send_message(
        f"✅ *Age filter saved:* `{age_min}–{age_max}`",
        parse_mode="Markdown",
    )

    await vip_state_menu(update, context)


# =========================
# STATE FILTER
# =========================
INDIAN_STATES = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa",
    "Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
    "Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland",
    "Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
    "Tripura","Uttar Pradesh","Uttarakhand","West Bengal",
    "Delhi","Jammu & Kashmir","Ladakh","Puducherry","Chandigarh"
]


async def vip_state_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    keyboard = [
        [InlineKeyboardButton(s, callback_data=f"vip_state:{s.replace(' ', '_')}")]
        for s in INDIAN_STATES
    ]

    await query.message.chat.send_message(
        "📍 *Select State*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def vip_state_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    user_id = str(query.from_user.id)
    state = query.data.split(":", 1)[1].replace("_", " ")

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET state=%s WHERE user_id=%s",
            (state, user_id),
        )
        conn.commit()
    conn.close()

    await query.message.chat.send_message(
        f"✅ *State filter saved:* `{state}`",
        parse_mode="Markdown",
    )

    await vip_language_menu(update, context)


# =========================
# LANGUAGE FILTER
# =========================
LANGUAGES = [
    "English","Hindi","Kannada","Tamil","Telugu","Malayalam","Marathi",
    "Gujarati","Punjabi","Bengali","Urdu","Spanish","French","German","Arabic"
]


async def vip_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    keyboard = [
        [InlineKeyboardButton(l, callback_data=f"vip_lang:{l}")]
        for l in LANGUAGES
    ]

    await query.message.chat.send_message(
        "🗣 *Select Language*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def vip_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    user_id = str(query.from_user.id)
    language = query.data.split(":", 1)[1]

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET language=%s WHERE user_id=%s",
            (language, user_id),
        )
        conn.commit()
    conn.close()

    await query.message.chat.send_message(
        f"✅ *Language filter saved:* `{language}`",
        parse_mode="Markdown",
    )

    keyboard = [
        [InlineKeyboardButton("🔍 Start Matching", callback_data="start_matching")]
    ]

    await query.message.chat.send_message(
        "🎉 *All preferences saved successfully!*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# VERIFIED ONLY FILTER
# =========================
async def vip_verified_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    user_id = str(query.from_user.id)

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET verified_only=TRUE WHERE user_id=%s",
            (user_id,),
        )
        conn.commit()
    conn.close()

    await query.message.chat.send_message(
        "✅ *Verified-only matching enabled*",
        parse_mode="Markdown",
    )


# =========================
# RESET ALL FILTERS
# =========================
async def vip_reset_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await delete_menu(query)

    user_id = str(query.from_user.id)

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE users
            SET age_min=NULL,
                age_max=NULL,
                state=NULL,
                language=NULL,
                verified_only=FALSE
            WHERE user_id=%s
            """,
            (user_id,),
        )
        conn.commit()
    conn.close()

    await query.message.chat.send_message(
        "🔄 *All filters reset.*\n\nYou can set new preferences anytime.",
        parse_mode="Markdown",
    )
