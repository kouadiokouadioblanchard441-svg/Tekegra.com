"""Per-user cooldown between signal generations (in-memory).

The timer is shared across all games: a Lucky Jet signal blocks Mines and
Rocket Queen too. A slot is reserved before generation so two simultaneous
callbacks cannot both create a prediction.
"""
import time

SIGNAL_COOLDOWN_SECONDS = 121  # 2 minutes 1 second

# {user_id: unix_timestamp_of_last_completed_or_reserved_signal}
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
    """Record that a signal was just generated for this user."""
    _last_signal_time[user_id] = time.time()


def release_signal_reservation(user_id: int) -> None:
    """Release a slot reserved for a request that could not be generated."""
    _last_signal_time.pop(user_id, None)


def reserve_signal(user_id: int) -> tuple[bool, float]:
    """Reserve the next signal slot atomically within the bot event loop.

    The reservation happens before any awaited generation work. This closes
    the race where a user taps two signal buttons before the first response
    has finished. ``record_signal`` may be called after successful generation
    to start the full cooldown from completion.
    """
    remaining = get_cooldown_remaining(user_id)
    if remaining > 0:
        return False, remaining
    _last_signal_time[user_id] = time.time()
    return True, 0.0


def format_cooldown_message(seconds: float) -> str:
    """Ready-to-send Telegram text when the user is in cooldown."""
    wait = _format_wait(seconds)
    return (
        f"⏳ *Signal temporairement indisponible*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"│◉ Prochain signal dans : *{wait}*\n"
        f"│◉ Reviens dans un moment 🕐\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 Tous les jeux partagent ce délai."
    )
