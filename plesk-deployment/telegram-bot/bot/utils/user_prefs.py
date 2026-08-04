"""Per-user in-memory preferences (survive until bot restart).

Currently stores the Lucky Jet cote preference: 'petite' (2X–5X) or
'grosse' (5X–20X).  The default is 'grosse' so existing users are not
surprised by a changed behaviour after upgrade.
"""

# {user_id: "petite" | "grosse"}
_cote_pref: dict[int, str] = {}


def get_cote_pref(user_id: int) -> str:
    """Return the saved cote preference, defaulting to 'grosse'."""
    return _cote_pref.get(user_id, "grosse")


def set_cote_pref(user_id: int, cote_type: str) -> None:
    """Save the cote preference for a user."""
    if cote_type in ("petite", "grosse"):
        _cote_pref[user_id] = cote_type
