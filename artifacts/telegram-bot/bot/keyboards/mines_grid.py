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

    # 5×5 grid rows
    for row_idx, row in enumerate(grid):
        button_row = []
        for col_idx, cell in enumerate(row):
            pos = row_idx * 5 + col_idx
            # All cells are non-interactive display buttons
            button_row.append(
                InlineKeyboardButton(
                    text=cell,
                    callback_data=f"mines:cell:{pos}:{cell}",
                )
            )
        buttons.append(button_row)

    # Action row below the grid
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
