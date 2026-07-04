from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def premium_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="⭐ Activer Premium — 7 jours", callback_data="premium:buy_7"),
        ],
        [
            InlineKeyboardButton(text="⭐⭐ Activer Premium — 30 jours", callback_data="premium:buy_30"),
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
