"""Signal generation engine for Lucky Jet, Rocket Queen and Mines."""
import random
from datetime import datetime, timedelta
import pytz


def _get_signal_time() -> str:
    """Generate a realistic future time for the signal."""
    now = datetime.now(pytz.UTC)
    offset = random.randint(30, 300)  # 30 s to 5 minutes ahead
    signal_time = now + timedelta(seconds=offset)
    return signal_time.strftime("%H:%M:%S")


def _get_countdown() -> int:
    """Seconds until the predicted game round starts (used for auto-delete)."""
    return random.randint(30, 180)


def _cote_for_type(cote_type: str, is_premium: bool, max_grosse: float) -> str:
    """Return a formatted multiplier string based on cote type."""
    if cote_type == "petite":
        # Small, frequent multipliers
        val = round(random.uniform(1.10, 2.80 if is_premium else 2.50), 2)
    elif cote_type == "grosse":
        # Big, rarer multipliers
        min_val = 3.00
        val = round(random.uniform(min_val, max_grosse), 2)
    else:
        # auto — legacy balanced behaviour
        if is_premium:
            buckets = [
                round(random.uniform(1.50, 3.0), 2),
                round(random.uniform(3.0, 8.0), 2),
                round(random.uniform(8.0, 25.0), 2),
            ]
            val = random.choices(buckets, weights=[40, 40, 20])[0]
        else:
            buckets = [
                round(random.uniform(1.50, 2.5), 2),
                round(random.uniform(2.5, 5.0), 2),
            ]
            val = random.choices(buckets, weights=[60, 40])[0]
    return f"{val}x"


def _assurance_for_type(cote_type: str) -> str:
    return "1.20X+" if cote_type == "petite" else "2.00X+"


def _get_niveau() -> str:
    return random.choice(["Faible", "Moyen", "Élevé"])


def _get_risque(niveau: str) -> str:
    return {"Faible": "Prudente", "Moyen": "Modérée", "Élevé": "Agressive"}.get(niveau, "Modérée")


# ─── Lucky Jet ───────────────────────────────────────────────────────────────

def generate_luckyjet_signal(is_premium: bool = False, cote_type: str = "auto") -> dict:
    """Generate a Lucky Jet prediction signal."""
    heure = _get_signal_time()
    cote = _cote_for_type(cote_type, is_premium, max_grosse=25.0 if is_premium else 15.0)
    niveau = _get_niveau()
    risque = _get_risque(niveau)
    assurance = _assurance_for_type(cote_type)
    countdown = _get_countdown()

    # Seconde précise pour placer la mise (ex: "à la 3ème seconde du round")
    mise_seconde = round(random.uniform(1.0, 3.5 if not is_premium else 5.0), 1)

    return {
        "heure": heure,
        "cote": cote,
        "assurance": assurance,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "cote_type": cote_type,
        "mise_seconde": mise_seconde,
    }


# ─── Rocket Queen ─────────────────────────────────────────────────────────────

def generate_rocketqueen_signal(is_premium: bool = False, cote_type: str = "auto") -> dict:
    """Generate a Rocket Queen prediction signal."""
    heure = _get_signal_time()
    cote = _cote_for_type(cote_type, is_premium, max_grosse=50.0 if is_premium else 20.0)
    niveau = _get_niveau()
    risque = _get_risque(niveau)
    assurance = _assurance_for_type(cote_type)
    countdown = _get_countdown()

    return {
        "heure": heure,
        "cote": cote,
        "assurance": assurance,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "cote_type": cote_type,
    }


# ─── Aviator ──────────────────────────────────────────────────────────────────

def generate_aviator_signal(is_premium: bool = False) -> dict:
    """Generate an Aviator prediction signal with precise time and cash-out second."""
    heure = _get_signal_time()
    countdown = _get_countdown()
    niveau = _get_niveau()
    risque = _get_risque(niveau)

    # Cash-out second: moment précis dans le round où retirer
    if is_premium:
        # Premium : cotes plus élevées, secondes plus tardives
        cashout_second = round(random.uniform(2.0, 8.0), 1)
        cote = round(random.choices(
            [random.uniform(1.5, 3.0), random.uniform(3.0, 8.0), random.uniform(8.0, 30.0)],
            weights=[35, 40, 25],
        )[0], 2)
    else:
        # Gratuit : cotes prudentes
        cashout_second = round(random.uniform(1.5, 4.5), 1)
        cote = round(random.choices(
            [random.uniform(1.3, 2.5), random.uniform(2.5, 5.0)],
            weights=[55, 45],
        )[0], 2)

    # Fenêtre de mise : intervalle en secondes avant le décollage
    mise_start = random.randint(3, 8)
    mise_end = mise_start + random.randint(2, 5)

    assurance = "1.30x+" if not is_premium else "2.00x+"

    return {
        "heure": heure,
        "cote": f"{cote}x",
        "cashout_second": cashout_second,
        "mise_start": mise_start,
        "mise_end": mise_end,
        "assurance": assurance,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
    }


# ─── Mines ────────────────────────────────────────────────────────────────────

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

    grid = _generate_mines_grid(mines_count=mines, is_premium=is_premium)

    return {
        "mines": mines,
        "safe_tiles": safe_tiles,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "grid": grid,
        "mine_positions": [
            i for i, cell in enumerate(sum(grid, []))
            if cell == "💣"
        ],
    }


def _generate_mines_grid(mines_count: int, is_premium: bool) -> list:
    """Build a 5×5 prediction grid for Mines."""
    GRID = 25
    positions = list(range(GRID))
    random.shuffle(positions)

    mine_positions = set(positions[:mines_count])
    safe_positions = positions[mines_count:]

    highlight_count = min(len(safe_positions), 5 if is_premium else 3)
    highlighted = set(safe_positions[:highlight_count])

    flat: list[str] = []
    for idx in range(GRID):
        if idx in mine_positions:
            flat.append("💣")
        elif idx in highlighted:
            flat.append("⭐")
        else:
            flat.append("🟦")

    return [flat[r * 5: r * 5 + 5] for r in range(5)]
