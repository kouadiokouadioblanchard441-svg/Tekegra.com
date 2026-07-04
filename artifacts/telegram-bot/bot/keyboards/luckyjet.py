from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def luckyjet_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🚀 Signal", callback_data="lj:signal_free"),
            InlineKeyboardButton(text="⭐ Signal Premium", callback_data="lj:signal_premium"),
        ],
        [
            InlineKeyboardButton(text="📊 Analyse IA", callback_data="lj:analyse"),
            InlineKeyboardButton(text="📈 Historique", callback_data="lj:history"),
        ],
        [
            InlineKeyboardButton(text="⬅ Retour", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def luckyjet_after_signal_keyboard(affiliate_link: str = "") -> InlineKeyboardMarkup:
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(text="🚀 Nouveau signal", callback_data="lj:signal_free"),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:luckyjet"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def luckyjet_after_premium_keyboard(affiliate_link: str = "") -> InlineKeyboardMarkup:
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(text="⭐ Nouveau signal premium", callback_data="lj:signal_premium"),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:luckyjet"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
