# bot/handlers/payments.py

import logging
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
)
from telegram.ext import ContextTypes

from bot.core.database import fetch_one, execute

logger = logging.getLogger(__name__)

# ======================================================
# VIP PLANS (Telegram Stars)
# ======================================================

VIP_PLANS = {
    "vip_lite_1d": {"title": "VIP Lite — 1 Day", "stars": 49, "days": 1, "tier": "VIP Lite"},
    "vip_lite_7d": {"title": "VIP Lite — 7 Days", "stars": 99, "days": 7, "tier": "VIP Lite"},
    "vip_30d": {"title": "VIP — 30 Days", "stars": 299, "days": 30, "tier": "VIP"},
    "vip_90d": {"title": "VIP — 3 Months", "stars": 899, "days": 90, "tier": "VIP"},
    "super_vip_180d": {"title": "Super VIP — 6 Months", "stars": 1799, "days": 180, "tier": "Super VIP"},
    "super_vip_365d": {"title": "Super VIP — 1 Year", "stars": 2999, "days": 365, "tier": "Super VIP"},
}

# ======================================================
# SHOW VIP MENU
# ======================================================

async def send_vip_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ VIP Lite", callback_data="vip:tier:lite")],
        [InlineKeyboardButton("⭐ VIP", callback_data="vip:tier:vip")],
        [InlineKeyboardButton("🔥 Super VIP", callback_data="vip:tier:super")],
    ]

    await update.effective_chat.send_message(
        text="⭐ *Choose your VIP tier:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# ======================================================
# SHOW PLANS
# ======================================================

async def vip_tier_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tier_map = {
        "vip:tier:lite": "VIP Lite",
        "vip:tier:vip": "VIP",
        "vip:tier:super": "Super VIP",
    }

    tier = tier_map.get(query.data)
    if not tier:
        return

    keyboard = [
        [InlineKeyboardButton(f"{p['title']} ⭐{p['stars']}", callback_data=f"vip:buy:{k}")]
        for k, p in VIP_PLANS.items() if p["tier"] == tier
    ]

    await query.message.edit_text(
        text=f"⭐ *{tier} plans:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# ======================================================
# SEND INVOICE
# ======================================================

async def send_vip_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_key = query.data.replace("vip:buy:", "")
    plan = VIP_PLANS.get(plan_key)
    if not plan:
        return

    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=plan["title"],
        description=f"Unlimited anonymous chats for {plan['days']} days",
        payload=plan_key,
        provider_token="",   # required empty for Stars
        currency="XTR",
        prices=[LabeledPrice(plan["title"], plan["stars"])],
    )

# ======================================================
# PRE-CHECKOUT (FAILED PAYMENTS LOGGED HERE)
# ======================================================

async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    plan_key = query.invoice_payload
    plan = VIP_PLANS.get(plan_key)

    # Always accept valid plans
    if plan:
        await query.answer(ok=True)
        return

    # ❌ Invalid / failed payment
    user_id = query.from_user.id
    amount = plan["stars"] if plan else 0

    await execute(
        """
        INSERT INTO payments (user_id, amount, provider, status)
        VALUES ($1, $2, 'telegram_stars', 'FAILED')
        """,
        user_id,
        amount,
    )

    logger.warning(f"PAYMENT FAILED | user={user_id} | payload={plan_key}")

    await query.answer(ok=False, error_message="Payment failed. Please try again.")

# ======================================================
# SUCCESSFUL PAYMENT
# ======================================================

async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    plan_key = payment.invoice_payload
    plan = VIP_PLANS.get(plan_key)
    if not plan:
        return

    user_id = update.effective_user.id
    now = datetime.utcnow()

    row = await fetch_one(
        "SELECT vip_until FROM users WHERE user_id = $1",
        user_id,
    )

    current_vip_until = row["vip_until"] if row and row["vip_until"] else None

    if current_vip_until and current_vip_until > now:
        new_vip_until = current_vip_until + timedelta(days=plan["days"])
    else:
        new_vip_until = now + timedelta(days=plan["days"])

    await execute(
        "UPDATE users SET vip_until = $1 WHERE user_id = $2",
        new_vip_until,
        user_id,
    )

    # ✅ SUCCESS PAYMENT LOG
    await execute(
        """
        INSERT INTO payments (user_id, amount, provider, status)
        VALUES ($1, $2, 'telegram_stars', 'SUCCESS')
        """,
        user_id,
        plan["stars"],
    )

    logger.info(
        f"PAYMENT SUCCESS | user={user_id} | tier={plan['tier']} | until={new_vip_until}"
    )

    await update.message.reply_text(
        f"🎉 *VIP Activated!*\n\n"
        f"Tier: {plan['tier']}\n"
        f"Valid until: {new_vip_until.strftime('%Y-%m-%d %H:%M UTC')}",
        parse_mode="Markdown",
    )
