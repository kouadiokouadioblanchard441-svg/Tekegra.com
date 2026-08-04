from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def mines_choose_keyboard(remaining: int, total: int) -> InlineKeyboardMarkup:
    """Écran de choix : Gratuit ou Premium."""
    if remaining > 0:
        free_label = f"💣 Signal Gratuit ({remaining}/{total} restants)"
    else:
        free_label = f"⛔ Gratuit épuisé ({total}/{total} utilisés)"

    buttons = [
        [InlineKeyboardButton(text=free_label, callback_data="mines:signal_free")],
        [InlineKeyboardButton(text="⭐ Signal Premium", callback_data="mines:signal_premium")],
        [InlineKeyboardButton(text="↩ Retour", callback_data="menu:mines")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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


def mines_premium_type_keyboard() -> InlineKeyboardMarkup:
    """Choix du mode d'étoiles Premium : Petite (2-5 ⭐) ou Grosse (6-10 ⭐)."""
    buttons = [
        [
            InlineKeyboardButton(text="🌟 Petite (2–5 ⭐)", callback_data="mines:signal_premium"),
            InlineKeyboardButton(text="💥 Grosse (6–10 ⭐)", callback_data="mines:signal_premium"),
        ],
        [InlineKeyboardButton(text="↩ Retour", callback_data="mines:choose_type")],
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
