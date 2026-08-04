"""Lucky Jet inline keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def luckyjet_choose_keyboard(remaining: int, total: int) -> InlineKeyboardMarkup:
    """Écran de choix : Gratuit ou Premium."""
    if remaining > 0:
        free_label = f"🎯 Signal Gratuit ({remaining}/{total} restants)"
    else:
        free_label = f"⛔ Gratuit épuisé ({total}/{total} utilisés)"

    buttons = [
        [InlineKeyboardButton(text=free_label, callback_data="lj:get_signal")],
        [
            InlineKeyboardButton(
                text="✈️ Petite Cote Premium",
                callback_data="lj:signal_premium:petite",
            ),
            InlineKeyboardButton(
                text="🚀 Grosse Cote Premium",
                callback_data="lj:signal_premium:grosse",
            ),
        ],
        [InlineKeyboardButton(text="↩ Retour", callback_data="menu:luckyjet")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def luckyjet_menu_keyboard() -> InlineKeyboardMarkup:
    """Menu principal Lucky Jet — gratuit = signal normal, pas de choix Petite/Grosse."""
    buttons = [
        [
            InlineKeyboardButton(text="🎯 Signal Gratuit", callback_data="lj:get_signal"),
        ],
        [
            InlineKeyboardButton(text="✈️ Petite Cote Premium", callback_data="lj:signal_premium:petite"),
            InlineKeyboardButton(text="🚀 Grosse Cote Premium", callback_data="lj:signal_premium:grosse"),
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
    """Boutons après un signal gratuit — pas de choix de type."""
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(
            text="🔄 Nouveau Signal",
            callback_data="lj:get_signal",
        ),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:luckyjet"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def luckyjet_after_premium_keyboard(
    affiliate_link: str = "",
    cote_type: str = "petite",
) -> InlineKeyboardMarkup:
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    label = "Petite Cote" if cote_type == "petite" else "Grosse Cote"
    buttons.append([
        InlineKeyboardButton(
            text=f"✈️ Nouveau signal premium {label}",
            callback_data=f"lj:signal_premium:{cote_type}",
        ),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:luckyjet"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
