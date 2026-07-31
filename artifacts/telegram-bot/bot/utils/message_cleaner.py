"""Keeps signal messages for ten minutes and replaces them on a new request.

Rules:
  • signal messages are sent as *new* messages (not edits).
  • a signal is automatically deleted after 600 seconds.
  • when a new signal is requested, delete_previous_signal() removes the old
    signal immediately, before the new one is displayed.
"""
import asyncio
import time
from loguru import logger

# {(chat_id, message_id): delete_at_unix_timestamp}
_pending: dict[tuple[int, int], float] = {}

# Last signal message per user: {user_id: (chat_id, message_id)}
_last_signal: dict[int, tuple[int, int]] = {}

_bot = None
SIGNAL_TTL_SECONDS = 10 * 60


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
    _pending.pop((chat_id, message_id), None)


def schedule_delete(chat_id: int, message_id: int, delete_in_seconds: float = SIGNAL_TTL_SECONDS) -> None:
    """Schedule a signal message for deletion after the configured TTL."""
    _pending[(chat_id, message_id)] = time.time() + delete_in_seconds


def track_signal_message(user_id: int, chat_id: int, message_id: int) -> None:
    """Remember the latest signal message for this user."""
    _last_signal[user_id] = (chat_id, message_id)


def clear_signal_tracking(user_id: int) -> None:
    """Clear the tracking for a user without deleting the message.

    Use this when the user navigates away from a signal (e.g. back to menu)
    and the signal message has been transformed in-place into a menu message.
    """
    _last_signal.pop(user_id, None)


async def _cleaner_loop() -> None:
    """Delete expired signals in the background."""
    while True:
        await asyncio.sleep(5)
        if not _pending or _bot is None:
            continue

        now = time.time()
        expired = [(key, deadline) for key, deadline in list(_pending.items()) if deadline <= now]
        for (chat_id, message_id), _ in expired:
            try:
                await _bot.delete_message(chat_id=chat_id, message_id=message_id)
                logger.debug(f"MessageCleaner: deleted expired signal msg {message_id}")
            except Exception:
                pass  # Already deleted or no permission — ignore silently
            _pending.pop((chat_id, message_id), None)
            for user_id, (tracked_chat_id, tracked_message_id) in list(_last_signal.items()):
                if tracked_chat_id == chat_id and tracked_message_id == message_id:
                    _last_signal.pop(user_id, None)


def start_cleaner(bot) -> None:
    """Attach the bot instance and start the expiry loop."""
    init_cleaner(bot)
    asyncio.create_task(_cleaner_loop())
    logger.info("✅ MessageCleaner started (signals expire after 10 minutes)")
