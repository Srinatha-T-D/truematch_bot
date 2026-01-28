# bot/utils/keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def intent_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for selecting intent (what user is looking for)
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="💬 Chat with Anyone",
                callback_data="intent:any"
            )
        ],
        [
            InlineKeyboardButton(
                text="👨 Chat with Men",
                callback_data="intent:male"
            ),
            InlineKeyboardButton(
                text="👩 Chat with Women",
                callback_data="intent:female"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def vip_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown when VIP is required
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="⭐ Upgrade to VIP",
                callback_data="vip:buy"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def consent_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown when no exact match is available.
    User explicitly chooses whether to relax preferences.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Yes",
                callback_data="consent_yes"
            ),
            InlineKeyboardButton(
                text="❌ No",
                callback_data="consent_no"
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def disconnect_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown during active chat
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="❌ Disconnect",
                callback_data="chat:disconnect"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def report_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown after chat for reporting
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="🚩 Report",
                callback_data="chat:report"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
