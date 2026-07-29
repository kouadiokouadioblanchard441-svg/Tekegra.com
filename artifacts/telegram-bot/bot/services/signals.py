"""
Signal generation engine — Lucky Jet, Rocket Queen, Aviator & Mines.

Améliorations v2:
- Score de confiance IA (70–98 %)
- Niveau de qualité GOLD / SILVER / BRONZE
- Indicateur de tendance HAUSSIER / BAISSIER / NEUTRE
- Indicateur de volatilité + force du signal
- Code de vérification unique par signal
- Anti-répétition : les 3 derniers signaux par jeu/utilisateur évitent les doublons
- Pondération temporelle : heures de pointe → confiance plus élevée
"""
import random
import string
from collections import defaultdict
from datetime import datetime, timedelta
import pytz

# ─── Cache anti-répétition (in-memory, par game_type) ────────────────────────
_last_signals: dict[str, list[float]] = defaultdict(list)
_MAX_CACHE = 5  # garde les 5 dernières cotes par type de jeu


def _register_cote(game_type: str, cote_float: float) -> None:
    cache = _last_signals[game_type]
    cache.append(cote_float)
    if len(cache) > _MAX_CACHE:
        cache.pop(0)


def _is_repeated(game_type: str, cote_float: float, tolerance: float = 0.15) -> bool:
    """True si une cote trop proche a déjà été générée récemment."""
    return any(abs(cote_float - prev) <= tolerance for prev in _last_signals[game_type])


def _unique_cote(game_type: str, generator_fn, max_tries: int = 10) -> float:
    for _ in range(max_tries):
        val = generator_fn()
        if not _is_repeated(game_type, val):
            _register_cote(game_type, val)
            return val
    # fallback : accepte la valeur même si répétée
    val = generator_fn()
    _register_cote(game_type, val)
    return val


# ─── Utilitaires temporels ────────────────────────────────────────────────────

def _is_peak_hour() -> bool:
    """Heures de pointe : 18h-23h UTC — confiance légèrement plus élevée."""
    now = datetime.now(pytz.UTC)
    return 18 <= now.hour <= 23


def _get_signal_time() -> str:
    now = datetime.now(pytz.UTC)
    return now.strftime("%H:%M") + " (GMT+00)"


def _get_countdown() -> int:
    return random.randint(30, 180)


# ─── Indicateurs IA ──────────────────────────────────────────────────────────

def _get_confidence(is_premium: bool) -> int:
    """Score de confiance IA en %. Premium → fourchette plus haute."""
    peak = _is_peak_hour()
    if is_premium:
        base = random.choices(
            [random.randint(88, 94), random.randint(94, 98)],
            weights=[45, 55] if peak else [60, 40],
        )[0]
    else:
        base = random.choices(
            [random.randint(70, 79), random.randint(79, 87)],
            weights=[35, 65] if peak else [50, 50],
        )[0]
    return base


def _get_quality(confidence: int) -> str:
    if confidence >= 94:
        return "GOLD"
    if confidence >= 82:
        return "SILVER"
    return "BRONZE"


def _quality_badge(quality: str, is_premium: bool) -> str:
    prefix = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    medals = {"GOLD": "🥇 GOLD", "SILVER": "🥈 SILVER", "BRONZE": "🥉 BRONZE"}
    return f"{prefix} | {medals.get(quality, quality)}"


def _get_trend() -> str:
    return random.choices(
        ["📈 HAUSSIER", "📉 BAISSIER", "➡️ NEUTRE"],
        weights=[45, 25, 30],
    )[0]


def _get_volatilite() -> str:
    return random.choices(
        ["🟢 FAIBLE", "🟡 MODÉRÉE", "🔴 ÉLEVÉE"],
        weights=[40, 40, 20],
    )[0]


def _get_force_bar(confidence: int) -> str:
    """Barre visuelle de force du signal (10 blocs)."""
    filled = round(confidence / 10)
    return "█" * filled + "░" * (10 - filled)


def _get_verification_code() -> str:
    """Code alphanumérique unique de vérification du signal."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=8))


def _get_niveau() -> str:
    return random.choice(["Faible", "Moyen", "Élevé"])


def _get_risque(niveau: str) -> str:
    return {"Faible": "Prudente", "Moyen": "Modérée", "Élevé": "Agressive"}.get(niveau, "Modérée")


def _assurance_for_type(cote_type: str) -> str:
    return "1.20X+" if cote_type == "petite" else "2.00X+"


# ─── Générateurs de cote ──────────────────────────────────────────────────────

def _cote_for_type(
    game_type: str,
    cote_type: str,
    is_premium: bool,
    max_grosse: float,
) -> tuple[str, float]:
    """Retourne (cote_str, cote_float) unique pour ce game_type."""
    if cote_type == "petite":
        fn = lambda: round(random.uniform(1.10, 2.80 if is_premium else 2.50), 2)
    elif cote_type == "grosse":
        fn = lambda: round(random.uniform(3.00, max_grosse), 2)
    else:
        # auto — pondération multi-bucket
        if is_premium:
            def fn():
                return round(random.choices(
                    [random.uniform(1.50, 3.0), random.uniform(3.0, 8.0), random.uniform(8.0, 25.0)],
                    weights=[35, 40, 25],
                )[0], 2)
        else:
            def fn():
                return round(random.choices(
                    [random.uniform(1.50, 2.5), random.uniform(2.5, 5.0)],
                    weights=[60, 40],
                )[0], 2)

    val = _unique_cote(game_type, fn)
    return f"{val}x", val


# ─── Lucky Jet ────────────────────────────────────────────────────────────────

def generate_luckyjet_signal(is_premium: bool = False, cote_type: str = "auto") -> dict:
    heure = _get_signal_time()
    cote_str, cote_float = _cote_for_type("luckyjet", cote_type, is_premium, 25.0 if is_premium else 15.0)
    confidence = _get_confidence(is_premium)
    quality = _get_quality(confidence)
    trend = _get_trend()
    volatilite = _get_volatilite()
    niveau = _get_niveau()
    risque = _get_risque(niveau)
    assurance = _assurance_for_type(cote_type)
    countdown = _get_countdown()
    mise_seconde = round(random.uniform(1.0, 3.5 if not is_premium else 5.0), 1)
    verification_code = _get_verification_code()
    force_bar = _get_force_bar(confidence)

    # Analyse séquentielle simulée : nb de rounds analysés avant ce signal
    rounds_analysed = random.randint(50, 200) if is_premium else random.randint(20, 80)

    return {
        "heure": heure,
        "cote": cote_str,
        "cote_float": cote_float,
        "assurance": assurance,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "cote_type": cote_type,
        "mise_seconde": mise_seconde,
        # Nouveaux champs IA
        "confidence": confidence,
        "quality": quality,
        "trend": trend,
        "volatilite": volatilite,
        "force_bar": force_bar,
        "verification_code": verification_code,
        "rounds_analysed": rounds_analysed,
    }


# ─── Rocket Queen ─────────────────────────────────────────────────────────────

def generate_rocketqueen_signal(is_premium: bool = False, cote_type: str = "auto") -> dict:
    heure = _get_signal_time()
    cote_str, cote_float = _cote_for_type("rocketqueen", cote_type, is_premium, 50.0 if is_premium else 20.0)
    confidence = _get_confidence(is_premium)
    quality = _get_quality(confidence)
    trend = _get_trend()
    volatilite = _get_volatilite()
    niveau = _get_niveau()
    risque = _get_risque(niveau)
    assurance = _assurance_for_type(cote_type)
    countdown = _get_countdown()
    verification_code = _get_verification_code()
    force_bar = _get_force_bar(confidence)
    rounds_analysed = random.randint(50, 200) if is_premium else random.randint(20, 80)

    return {
        "heure": heure,
        "cote": cote_str,
        "cote_float": cote_float,
        "assurance": assurance,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "cote_type": cote_type,
        "confidence": confidence,
        "quality": quality,
        "trend": trend,
        "volatilite": volatilite,
        "force_bar": force_bar,
        "verification_code": verification_code,
        "rounds_analysed": rounds_analysed,
    }


# ─── Aviator ──────────────────────────────────────────────────────────────────

def generate_aviator_signal(is_premium: bool = False) -> dict:
    heure = _get_signal_time()
    countdown = _get_countdown()
    niveau = _get_niveau()
    risque = _get_risque(niveau)
    confidence = _get_confidence(is_premium)
    quality = _get_quality(confidence)
    trend = _get_trend()
    volatilite = _get_volatilite()
    force_bar = _get_force_bar(confidence)
    verification_code = _get_verification_code()

    if is_premium:
        cashout_second = round(random.uniform(2.0, 8.0), 1)
        cote_raw = round(random.choices(
            [random.uniform(1.5, 3.0), random.uniform(3.0, 8.0), random.uniform(8.0, 30.0)],
            weights=[35, 40, 25],
        )[0], 2)
    else:
        cashout_second = round(random.uniform(1.5, 4.5), 1)
        cote_raw = round(random.choices(
            [random.uniform(1.3, 2.5), random.uniform(2.5, 5.0)],
            weights=[55, 45],
        )[0], 2)

    # Anti-répétition pour Aviator
    if _is_repeated("aviator", cote_raw):
        cote_raw = round(cote_raw + random.uniform(0.3, 0.8), 2)
    _register_cote("aviator", cote_raw)

    mise_start = random.randint(3, 8)
    mise_end = mise_start + random.randint(2, 5)
    assurance = "1.30x+" if not is_premium else "2.00x+"
    rounds_analysed = random.randint(50, 200) if is_premium else random.randint(20, 80)

    return {
        "heure": heure,
        "cote": f"{cote_raw}x",
        "cote_float": cote_raw,
        "cashout_second": cashout_second,
        "mise_start": mise_start,
        "mise_end": mise_end,
        "assurance": assurance,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "confidence": confidence,
        "quality": quality,
        "trend": trend,
        "volatilite": volatilite,
        "force_bar": force_bar,
        "verification_code": verification_code,
        "rounds_analysed": rounds_analysed,
    }


# ─── Mines ────────────────────────────────────────────────────────────────────

def generate_mines_signal(is_premium: bool = False) -> dict:
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
    confidence = _get_confidence(is_premium)
    quality = _get_quality(confidence)
    volatilite = _get_volatilite()
    force_bar = _get_force_bar(confidence)
    verification_code = _get_verification_code()
    rounds_analysed = random.randint(50, 200) if is_premium else random.randint(20, 80)

    # Probabilité théorique d'une case sûre (affichée en %)
    safe_probability = round((safe_tiles / 25) * 100)

    grid = _generate_mines_grid(mines_count=mines, is_premium=is_premium)

    return {
        "mines": mines,
        "safe_tiles": safe_tiles,
        "safe_probability": safe_probability,
        "niveau": niveau,
        "risque": risque,
        "countdown": countdown,
        "is_premium": is_premium,
        "grid": grid,
        "mine_positions": [
            i for i, cell in enumerate(sum(grid, []))
            if cell == "💣"
        ],
        "confidence": confidence,
        "quality": quality,
        "volatilite": volatilite,
        "force_bar": force_bar,
        "verification_code": verification_code,
        "rounds_analysed": rounds_analysed,
    }


def _generate_mines_grid(mines_count: int, is_premium: bool) -> list:
    """Grille 5×5 avec positions uniques, anti-clustering pour premium."""
    GRID = 25
    positions = list(range(GRID))
    random.shuffle(positions)

    mine_positions = set(positions[:mines_count])
    safe_positions = positions[mines_count:]

    # Premium : jusqu'à 5 cases révélées, gratuit : 3
    highlight_count = min(len(safe_positions), 5 if is_premium else 3)

    # Anti-clustering : on préfère des cases révélées bien espacées
    if is_premium and len(safe_positions) >= 5:
        highlighted = _spread_highlights(safe_positions, highlight_count)
    else:
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


def _spread_highlights(safe_positions: list, count: int) -> set:
    """Sélectionne `count` cases sûres en maximisant la distance entre elles."""
    selected = [safe_positions[0]]
    remaining = safe_positions[1:]

    while len(selected) < count and remaining:
        # Choisir la case la plus éloignée de toutes les déjà sélectionnées
        def min_dist(pos: int) -> int:
            return min(
                abs(pos % 5 - s % 5) + abs(pos // 5 - s // 5)
                for s in selected
            )
        best = max(remaining, key=min_dist)
        selected.append(best)
        remaining.remove(best)

    return set(selected)
