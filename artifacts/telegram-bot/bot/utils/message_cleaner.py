"""Tracks signal messages per user and deletes the previous one when a new one is requested.

Rules:
  • signal messages are sent as *new* messages (not edits).
  • when a new signal is requested, delete_previous_signal() removes the old one first.
  • signals are never auto-deleted by a timer — they stay until the next request.
"""
import asyncio
from loguru import logger

# Last signal message per user: {user_id: (chat_id, message_id)}
_last_signal: dict[int, tuple[int, int]] = {}

_bot = None


def init_cleaner(bot) -> None:
    """Call once at startup to attach the bot instance."""
    global _bot
    _bot = bot


async def delete_previous_signal(user_id: int) -> None:
    """Delete the last signal message for this user (if any), then clear tracking."""
    key = _last_signal.pop(user_id, None)
    if key is None or _bot is None:
        return
    chat_id, message_id = key
    try:
        await _bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.debug(f"MessageCleaner: deleted previous signal msg {message_id} for user {user_id}")
    except Exception:
        pass  # Already deleted or bot lacks permission — ignore silently


def track_signal_message(user_id: int, chat_id: int, message_id: int) -> None:
    """Remember the latest signal message for this user."""
    _last_signal[user_id] = (chat_id, message_id)


def clear_signal_tracking(user_id: int) -> None:
    """Clear the tracking for a user without deleting the message.

    Use this when the user navigates away from a signal (e.g. back to menu)
    and the signal message has been transformed in-place into a menu message.
    """
    _last_signal.pop(user_id, None)


def start_cleaner(bot) -> None:
    """Attach the bot instance. No background loop needed anymore."""
    init_cleaner(bot)
    logger.info("✅ MessageCleaner started (on-demand deletion mode)")
