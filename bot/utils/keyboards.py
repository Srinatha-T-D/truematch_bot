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

def report_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🚩 Report", callback_data="chat:report")]]
    )
