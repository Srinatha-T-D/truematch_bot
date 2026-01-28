# bot/handlers/verify_steps.py
# Handles verification step-by-step (name → gender → contact → captcha → DB save)

import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from bot.utils.logger import logger
from bot.services.verification_service import VerificationService


# =====================================
# TEXT HANDLER
# =====================================
async def verify_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()

    verify = context.user_data.get("verify")
    if not verify:
        return

    step = verify.get("step")

    # ---------------------------
    # STEP 1 → FULL NAME
    # ---------------------------
    if step == "full_name":
        if len(text) < 3:
            await update.message.reply_text(
                "❌ Name seems too short.\n\nPlease enter your *full name*.",
                parse_mode="Markdown",
            )
            return

        verify["full_name"] = text
        verify["step"] = "gender"

        keyboard = [
            [
                InlineKeyboardButton("👨 Male", callback_data="verify_gender:male"),
                InlineKeyboardButton("👩 Female", callback_data="verify_gender:female"),
            ],
            [
                InlineKeyboardButton("🌈 Other", callback_data="verify_gender:other"),
            ],
        ]

        await update.message.reply_text(
            "✅ *Name saved.*\n\nPlease select your *gender*:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
        return

    # ---------------------------
    # STEP 3 → CONTACT
    # ---------------------------
    if step == "contact":
        if "@" in text:
            contact_type = "email"
        elif text.replace("+", "").isdigit() and len(text) >= 8:
            contact_type = "phone"
        else:
            await update.message.reply_text(
                "❌ Invalid contact.\n\n"
                "Please enter a valid *phone number* or *email address*.",
                parse_mode="Markdown",
            )
            return

        verify["contact"] = text
        verify["contact_type"] = contact_type

        # ---------------------------
        # STEP 4 → CAPTCHA
        # ---------------------------
        a = random.randint(2, 9)
        b = random.randint(1, 9)

        verify["captcha"] = {
            "question": f"{a} + {b}",
            "answer": str(a + b),
        }
        verify["step"] = "captcha"

        logger.info(
            "[VERIFY] user=%s captcha_question=%s",
            user_id,
            verify["captcha"]["question"],
        )

        await update.message.reply_text(
            "🧠 *Anti-Bot Check*\n\n"
            f"Please answer:\n\n"
            f"👉 *{a} + {b} = ?*",
            parse_mode="Markdown",
        )
        return

    # ---------------------------
    # STEP 4 → CAPTCHA ANSWER
    # ---------------------------
    if step == "captcha":
        expected = verify.get("captcha", {}).get("answer")

        if text != expected:
            await update.message.reply_text(
                "❌ Incorrect answer.\n\nPlease try again:",
                parse_mode="Markdown",
            )
            return

        # ---------------------------
        # STEP 5 → SAVE TO DB
        # ---------------------------
        if VerificationService.has_pending_request(user_id):
            await update.message.reply_text(
                "⏳ You already have a verification request under review.\n\n"
                "Please wait for admin approval.",
                parse_mode="Markdown",
            )
            context.user_data.pop("verify", None)
            return

        VerificationService.create_request(
            user_id=user_id,
            full_name=verify["full_name"],
            gender=verify["gender"],
            contact=verify["contact"],
        )

        context.user_data.pop("verify", None)

        logger.info("[VERIFY] user=%s verification submitted", user_id)

        await update.message.reply_text(
            "✅ *Verification submitted successfully!*\n\n"
            "👮 Our admin team will review your details.\n"
            "⏳ Status: *Pending approval*\n\n"
            "You will be notified once verified.",
            parse_mode="Markdown",
        )
        return


# =====================================
# CALLBACK HANDLER (GENDER)
# =====================================
async def verify_gender_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    verify = context.user_data.get("verify")
    if not verify or verify.get("step") != "gender":
        return

    gender = query.data.split(":", 1)[1]
    verify["gender"] = gender
    verify["step"] = "contact"

    logger.info("[VERIFY] gender selected user=%s gender=%s", query.from_user.id, gender)

    await query.message.reply_text(
        "✅ *Gender saved.*\n\n"
        "Please enter your *phone number or email address*.\n\n"
        "🔒 This will be visible no one, dont worry.",
        parse_mode="Markdown",
    )
