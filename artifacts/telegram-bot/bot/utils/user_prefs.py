"""Per-user in-memory preferences (survive until bot restart).

Stores:
- Lucky Jet cote preference: 'petite' (2X–5X) or 'grosse' (5X–20X)
- Mines star preference: 'petite' (2–5 ⭐) or 'grosse' (6–10 ⭐)
Defaults to 'grosse' so existing users keep the previous behaviour.
"""

# {user_id: "petite" | "grosse"}
_cote_pref: dict[int, str] = {}
_star_pref: dict[int, str] = {}


def get_cote_pref(user_id: int) -> str:
    """Return the saved Lucky Jet cote preference, defaulting to 'grosse'."""
    return _cote_pref.get(user_id, "grosse")


def set_cote_pref(user_id: int, cote_type: str) -> None:
    """Save the Lucky Jet cote preference for a user."""
    if cote_type in ("petite", "grosse"):
        _cote_pref[user_id] = cote_type


def get_star_pref(user_id: int) -> str:
    """Return the saved Mines star preference, defaulting to 'grosse'."""
    return _star_pref.get(user_id, "grosse")


def set_star_pref(user_id: int, mode: str) -> None:
    """Save the Mines star preference for a user."""
    if mode in ("petite", "grosse"):
        _star_pref[user_id] = mode
