"""Signal generation engine for Lucky Jet and Mines."""
import random
from datetime import datetime, timedelta
import pytz


def _get_signal_time() -> str:
    """Generate a realistic future time for the signal."""
    now = datetime.now(pytz.UTC)
    offset = random.randint(30, 300)  # 30s to 5 minutes ahead
    signal_time = now + timedelta(seconds=offset)
    return signal_time.strftime("%H:%M:%S")


def _get_countdown() -> int:
    """Seconds until next signal is available."""
    return random.randint(30, 180)


def _get_luckyjet_cote(is_premium: bool) -> str:
    """Generate a multiplier. Premium gets higher potential odds."""
    if is_premium:
        # Premium: wider range, potentially huge multipliers
        choices = [
            round(random.uniform(1.5, 3.0), 2),
            round(random.uniform(3.0, 8.0), 2),
            round(random.uniform(8.0, 25.0), 2),
        ]
        weights = [40, 40, 20]
    else:
        # Free: more conservative
        choices = [
            round(random.uniform(1.5, 2.5), 2),
            round(random.uniform(2.5, 5.0), 2),
        ]
        weights = [60, 40]
    cote = random.choices(choices, weights=weights)[0]
    return f"{cote}x"


def _get_niveau() -> str:
    return random.choice(["Faible", "Moyen", "Élevé"])


def _get_risque(niveau: str) -> str:
    mapping = {
        "Faible": "Prudente",
        "Moyen": "Modérée",
        "Élevé": "Agressive",
    }
    return mapping.get(niveau, "Modérée")


def generate_luckyjet_signal(is_premium: bool = False) -> dict:
    """Generate a Lucky Jet prediction signal."""
    heure = _get_signal_time()
    cote = _get_luckyjet_cote(is_premium)
    niveau = _get_niveau()
    risque = _get_risque(niveau)
    assurance = "1.50X+"
    countdown = _get_countdown()

    return {
        "heure": heure,
        "cote": cote,
        "assurance": assurance,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
    }


def generate_mines_signal(is_premium: bool = False) -> dict:
    """Generate a Mines game analysis signal with a full 5x5 grid."""
    if is_premium:
        mines_options = [1, 2, 3, 5, 10, 15]
        weights = [10, 20, 30, 25, 10, 5]
    else:
        mines_options = [1, 2, 3, 5]
        weights = [15, 30, 35, 20]

    mines = random.choices(mines_options, weights=weights)[0]
    niveau = _get_niveau()
    risque = _get_risque(niveau)
    countdown = _get_countdown()
    safe_tiles = 25 - mines

    # Generate 5x5 grid with safe and mine positions
    grid = _generate_mines_grid(mines_count=mines, is_premium=is_premium)

    return {
        "mines": mines,
        "safe_tiles": safe_tiles,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "grid": grid,          # 5x5 list of lists with "⭐" | "🟦" | "💣"
        "mine_positions": [    # flat list of 0-24 indices that are mines
            i for i, cell in enumerate(sum(grid, []))
            if cell == "💣"
        ],
    }


def _generate_mines_grid(mines_count: int, is_premium: bool) -> list:
    """Build a 5x5 grid.

    Layout:
      ⭐  — recommended safe tile (AI prediction, revealed)
      💣  — mine position (revealed so user can avoid it)
      🟦  — neutral closed tile (safe but not highlighted)

    The bot always reveals ALL mine positions and a set of top safe spots,
    so the user knows exactly where to click.
    """
    GRID = 25  # 5×5

    # Shuffle all tile indices to assign roles randomly
    positions = list(range(GRID))
    random.shuffle(positions)

    mine_positions = set(positions[:mines_count])
    safe_positions = positions[mines_count:]

    # How many safe tiles to highlight with ⭐
    # Premium gets more highlighted tiles (clearer predictions)
    highlight_count = min(len(safe_positions), 5 if is_premium else 3)
    highlighted = set(safe_positions[:highlight_count])

    # Build flat array then reshape to 5×5
    flat: list[str] = []
    for idx in range(GRID):
        if idx in mine_positions:
            flat.append("💣")
        elif idx in highlighted:
            flat.append("⭐")
        else:
            flat.append("🟦")

    # Reshape to 5 rows × 5 cols
    return [flat[r * 5: r * 5 + 5] for r in range(5)]
