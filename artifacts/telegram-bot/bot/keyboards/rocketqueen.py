"""Rocket Queen game keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def rocketqueen_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🎯 Petite Cote (gratuit)", callback_data="rq:signal_free:petite"),
            InlineKeyboardButton(text="💰 Grosse Cote (gratuit)", callback_data="rq:signal_free:grosse"),
        ],
        [
            InlineKeyboardButton(text="⭐ Petite Cote Premium", callback_data="rq:signal_premium:petite"),
            InlineKeyboardButton(text="⭐ Grosse Cote Premium", callback_data="rq:signal_premium:grosse"),
        ],
        [
            InlineKeyboardButton(text="📊 Analyse IA", callback_data="rq:analyse"),
            InlineKeyboardButton(text="📈 Historique", callback_data="rq:history"),
        ],
        [
            InlineKeyboardButton(text="⬅ Retour", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def rocketqueen_after_signal_keyboard(
    affiliate_link: str = "",
    cote_type: str = "petite",
) -> InlineKeyboardMarkup:
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(
            text="🔄 Nouveau signal",
            callback_data=f"rq:signal_free:{cote_type}",
        ),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:rocketqueen"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def rocketqueen_after_premium_keyboard(
    affiliate_link: str = "",
    cote_type: str = "petite",
) -> InlineKeyboardMarkup:
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(
            text="⭐ Nouveau signal premium",
            callback_data=f"rq:signal_premium:{cote_type}",
        ),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:rocketqueen"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
