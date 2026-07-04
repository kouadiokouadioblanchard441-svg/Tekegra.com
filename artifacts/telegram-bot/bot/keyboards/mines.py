from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def mines_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="💣 Signal", callback_data="mines:signal_free"),
            InlineKeyboardButton(text="⭐ Signal Premium", callback_data="mines:signal_premium"),
        ],
        [
            InlineKeyboardButton(text="📊 Analyse IA", callback_data="mines:analyse"),
            InlineKeyboardButton(text="📈 Historique", callback_data="mines:history"),
        ],
        [
            InlineKeyboardButton(text="⬅ Retour", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def mines_after_signal_keyboard(affiliate_link: str = "") -> InlineKeyboardMarkup:
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(text="💣 Nouveau signal", callback_data="mines:signal_free"),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:mines"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
