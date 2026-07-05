"""Main menu keyboards — matches the screenshot layout."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ── Main menu  ────────────────────────────────────────────────────────────────
def main_menu_keyboard(affiliate_link: str = "") -> InlineKeyboardMarkup:
    """Screenshot layout: [Inscription][Guide] / [Modifier langue] / [GET SIGNAL]"""
    row1 = []
    if affiliate_link:
        row1.append(InlineKeyboardButton(text="Inscription", url=affiliate_link))
    else:
        row1.append(InlineKeyboardButton(text="Inscription", callback_data="menu:noop"))
    row1.append(InlineKeyboardButton(text="Guide", callback_data="menu:guide"))

    return InlineKeyboardMarkup(inline_keyboard=[
        row1,
        [InlineKeyboardButton(text="Modifier la langue", callback_data="menu:language")],
        [InlineKeyboardButton(text="GET SIGNAL", callback_data="menu:get_signal")],
    ])


# ── Registration page (user not yet registered on 1WIN) ───────────────────────
def register_keyboard(affiliate_link: str = "") -> InlineKeyboardMarkup:
    buttons = []
    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(text="📱 💠 S'inscrire sur 1WIN ↗", url=affiliate_link),
        ])
    buttons.append([
        InlineKeyboardButton(
            text="✅ J'ai créé mon compte",
            callback_data="menu:confirm_registered",
        ),
    ])
    buttons.append([
        InlineKeyboardButton(text="↩ Back to Main Menu", callback_data="menu:main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Game selection (after registration confirmed) ─────────────────────────────
def game_select_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 Lucky Jet", callback_data="menu:luckyjet"),
            InlineKeyboardButton(text="💣 Mines", callback_data="menu:mines"),
        ],
        [InlineKeyboardButton(text="↩ Back", callback_data="menu:main")],
    ])


# ── Lucky Jet signal page ─────────────────────────────────────────────────────
def luckyjet_page_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 GET SIGNAL", callback_data="lj:get_signal")],
        [InlineKeyboardButton(text="↩ Back", callback_data="menu:game_select")],
    ])


# ── Mines signal page ─────────────────────────────────────────────────────────
def mines_page_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💣 GET SIGNAL", callback_data="mines:get_signal")],
        [InlineKeyboardButton(text="↩ Back", callback_data="menu:game_select")],
    ])


# ── After-signal keyboards ────────────────────────────────────────────────────
def luckyjet_after_signal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Nouveau Signal", callback_data="lj:get_signal")],
        [InlineKeyboardButton(text="↩ Back", callback_data="menu:luckyjet")],
    ])


def mines_after_signal_keyboard_simple() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Nouvelle Grille", callback_data="mines:get_signal")],
        [InlineKeyboardButton(text="↩ Back", callback_data="menu:mines")],
    ])


# ── Language selection ────────────────────────────────────────────────────────
def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
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
        [InlineKeyboardButton(text="↩ Retour", callback_data="menu:main")],
    ])


# ── Guide keyboard ────────────────────────────────────────────────────────────
def guide_keyboard(
    affiliate_link: str = "",
    channel_1_link: str = "",
    channel_1_name: str = "📢 Canal Officiel",
    channel_2_link: str = "",
    channel_2_name: str = "📢 Canal Signaux VIP",
) -> InlineKeyboardMarkup:
    buttons = []
    if channel_1_link:
        buttons.append([InlineKeyboardButton(text=channel_1_name, url=channel_1_link)])
    if channel_2_link:
        buttons.append([InlineKeyboardButton(text=channel_2_name, url=channel_2_link)])
    if affiliate_link:
        buttons.append([InlineKeyboardButton(text="📝 INSCRIPTION ↗", url=affiliate_link)])
        buttons.append([InlineKeyboardButton(text="💳 RECHARGER ↗", url=affiliate_link)])
    buttons.append([InlineKeyboardButton(text="↩ Retour au menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Generic back-to-main ──────────────────────────────────────────────────────
def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩ Retour au menu", callback_data="menu:main")],
    ])
