from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard(affiliate_link: str = "") -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🎯 Lucky Jet", callback_data="menu:luckyjet"),
            InlineKeyboardButton(text="💣 Mines", callback_data="menu:mines"),
        ],
        [
            InlineKeyboardButton(text="👤 Mon profil", callback_data="menu:profile"),
            InlineKeyboardButton(text="⭐ Premium", callback_data="menu:premium"),
        ],
        [
            InlineKeyboardButton(text="📚 Guide", callback_data="menu:guide"),
            InlineKeyboardButton(text="🌍 Langue", callback_data="menu:language"),
        ],
        [
            InlineKeyboardButton(text="☎ Support", callback_data="menu:support"),
        ],
    ]
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def language_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang:fr"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        ],
        [
            InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang:ar"),
            InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang:es"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇧🇷 Português", callback_data="lang:pt"),
        ],
        [
            InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang:tr"),
            InlineKeyboardButton(text="🇮🇳 हिंदी", callback_data="lang:hi"),
        ],
        [
            InlineKeyboardButton(text="◀ Retour", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Retour au menu", callback_data="menu:main")]
    ])
