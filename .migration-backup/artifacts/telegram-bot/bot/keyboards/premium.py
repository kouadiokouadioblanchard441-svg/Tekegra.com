from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def premium_keyboard(price_7: str = "5 594 F", price_30: str = "16 794 F") -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"⭐ Premium 7 jours — {price_7}",
                callback_data="premium:buy_7",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"⭐⭐ Premium 30 jours — {price_30}",
                callback_data="premium:buy_30",
            ),
        ],
        [
            InlineKeyboardButton(text="📜 Mon abonnement", callback_data="premium:status"),
        ],
        [
            InlineKeyboardButton(text="⬅ Retour", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def premium_locked_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="⭐ Passer Premium maintenant", callback_data="menu:premium"),
        ],
        [
            InlineKeyboardButton(text="⬅ Retour", callback_data="menu:luckyjet"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
