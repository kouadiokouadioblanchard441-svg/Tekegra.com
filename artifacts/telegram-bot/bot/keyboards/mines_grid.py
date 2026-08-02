"""5×5 inline keyboard grid for the Mines game prediction."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def mines_grid_keyboard(
    grid: list[list[str]],
    is_premium: bool = False,
    affiliate_link: str = "",
) -> InlineKeyboardMarkup:
    """
    Build a 5×5 inline keyboard from the grid matrix.

    grid cells:
      ⭐  — AI-recommended safe tile to click
      💣  — mine position (avoid this tile)
      🟦  — unknown / neutral closed tile
    """
    buttons = []

    # Action row — grid is now displayed as text in the message body
    action_row = [
        InlineKeyboardButton(text="🔄 Nouveau signal", callback_data="mines:signal_free"),
        InlineKeyboardButton(text="⬅ Menu", callback_data="menu:mines"),
    ]
    if is_premium:
        action_row[0] = InlineKeyboardButton(
            text="⭐ Nouveau signal premium", callback_data="mines:signal_premium"
        )
    buttons.append(action_row)

    if affiliate_link:
        buttons.append([
            InlineKeyboardButton(
                text="🎰 Créer un compte 1WIN ↗", url=affiliate_link
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
