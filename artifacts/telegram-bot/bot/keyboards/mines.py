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


def mines_premium_type_keyboard(current: str = "grosse") -> InlineKeyboardMarkup:
    """Réglage du mode d'étoiles : Petite (2–5 ⭐) ou Grosse (6–10 ⭐).

    Shown immediately when the user selects Mines from the game selection.
    The chosen mode is saved to user_prefs and used for all subsequent signals.
    """
    petite_label = "✅ 🌟 Petite (2–5 ⭐)" if current == "petite" else "🌟 Petite (2–5 ⭐)"
    grosse_label = "✅ 💥 Grosse (6–10 ⭐)" if current == "grosse" else "💥 Grosse (6–10 ⭐)"
    buttons = [
        [
            InlineKeyboardButton(text=petite_label, callback_data="mines:set_mode:petite"),
            InlineKeyboardButton(text=grosse_label, callback_data="mines:set_mode:grosse"),
        ],
        [InlineKeyboardButton(text="↩ Retour", callback_data="menu:game_select")],
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
