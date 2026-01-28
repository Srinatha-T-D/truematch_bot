from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.services.vip_features.verification import VipVerificationService


async def show_verification_ui(query, context):
    user_id = query.from_user.id
    is_verified = await VipVerificationService.is_verified(user_id)

    if is_verified:
        await query.edit_message_text(
            "🔒 *Profile Verified*\n\n"
            "Your profile is verified and trusted.",
            parse_mode="Markdown"
        )
        return

    keyboard = [
        [InlineKeyboardButton("🔒 Request Verification", callback_data="request_verify")]
    ]

    await query.edit_message_text(
        "🔒 *Profile Verification*\n\n"
        "Verification increases trust.\n"
        "Admin approval required.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
