"""Per-user cooldown between free signal generations (in-memory).

The timer is shared across all games: a Lucky Jet signal blocks Mines too.
Premium users bypass the cooldown entirely.
"""
import time

SIGNAL_COOLDOWN_SECONDS = 121  # 2 minutes 1 second

# {user_id: unix_timestamp_of_last_free_signal}
_last_signal_time: dict[int, float] = {}


def _format_wait(seconds: float) -> str:
    """Human-readable wait time: '2m 01s' or '45s'."""
    total = int(seconds)
    m, s = divmod(total, 60)
    if m > 0:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def get_cooldown_remaining(user_id: int) -> float:
    """Return seconds still remaining in cooldown, or 0.0 if ready."""
    last = _last_signal_time.get(user_id, 0.0)
    remaining = SIGNAL_COOLDOWN_SECONDS - (time.time() - last)
    return max(0.0, remaining)


def record_signal(user_id: int) -> None:
    """Record that a free signal was just generated for this user."""
    _last_signal_time[user_id] = time.time()


def format_cooldown_message(seconds: float) -> str:
    """Ready-to-send Telegram text when the user is in cooldown."""
    wait = _format_wait(seconds)
    return (
        f"⏳ *Signal temporairement indisponible*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"│◉ Prochain signal dans : *{wait}*\n"
        f"│◉ Reviens dans un moment 🕐\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⭐ Les membres *Premium* n'ont aucune attente !"
    )
