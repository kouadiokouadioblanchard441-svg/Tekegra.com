"""Lucky Jet inline keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def luckyjet_choose_keyboard(remaining: int, total: int) -> InlineKeyboardMarkup:
    """Écran de choix : Gratuit ou Premium — sans mention de la cote."""
    if remaining > 0:
        free_label = f"🎯 Signal Gratuit ({remaining}/{total} restants)"
    else:
        free_label = f"⛔ Gratuit épuisé ({total}/{total} utilisés)"

    buttons = [
        [InlineKeyboardButton(text=free_label, callback_data="lj:get_signal")],
        [InlineKeyboardButton(text="⭐ Signal Premium", callback_data="lj:signal_premium")],
        [InlineKeyboardButton(text="↩ Retour", callback_data="menu:luckyjet")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def luckyjet_menu_keyboard() -> InlineKeyboardMarkup:
    """Menu principal Lucky Jet."""
    buttons = [
        [
            InlineKeyboardButton(text="🔥 Signal", callback_data="lj:get_signal"),
            InlineKeyboardButton(text="⚙️ Réglage", callback_data="lj:reglage"),
        ],
        [
            InlineKeyboardButton(text="⬅ Retour", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def luckyjet_reglage_keyboard(current: str = "grosse") -> InlineKeyboardMarkup:
    """Écran de réglage : choix de la plage de coefficient."""
    petite_label = "✅ 2X - 5X" if current == "petite" else "2X - 5X"
    grosse_label = "✅ 5X - 20X" if current == "grosse" else "5X - 20X"
    buttons = [
        [
            InlineKeyboardButton(text=petite_label, callback_data="lj:set_cote:petite"),
            InlineKeyboardButton(text=grosse_label, callback_data="lj:set_cote:grosse"),
        ],
        [
            InlineKeyboardButton(text="⬅ Retour", callback_data="menu:game_select"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def luckyjet_after_signal_keyboard(affiliate_link: str = "") -> InlineKeyboardMarkup:
    """Boutons après un signal — avec bouton Réglage."""
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="🎰 Créer un compte 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(text="🔄 Nouveau Signal", callback_data="lj:get_signal"),
        InlineKeyboardButton(text="⚙️ Réglage", callback_data="lj:reglage"),
    ])
    buttons.append([
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
    buttons.append([
        InlineKeyboardButton(
            text="⭐ Nouveau signal premium",
            callback_data="lj:signal_premium",
        ),
        InlineKeyboardButton(text="⚙️ Réglage", callback_data="lj:reglage"),
    ])
    buttons.append([
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:luckyjet"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
