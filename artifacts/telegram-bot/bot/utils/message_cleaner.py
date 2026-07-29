"""Background task that auto-deletes signal messages after game time + 2 minutes.

Also tracks the last signal message per user so that requesting a new signal
immediately removes the previous one.
"""
import asyncio
import time
from loguru import logger

# {(chat_id, message_id): delete_at_unix_timestamp}
_pending: dict[tuple[int, int], float] = {}

# Last signal message per user: {user_id: (chat_id, message_id)}
_last_signal: dict[int, tuple[int, int]] = {}

_bot = None


def init_cleaner(bot) -> None:
    """Call once at startup to attach the bot instance."""
    global _bot
    _bot = bot


def schedule_delete(chat_id: int, message_id: int, delete_in_seconds: float) -> None:
    """Schedule a message for deletion after N seconds."""
    delete_at = time.time() + delete_in_seconds
    _pending[(chat_id, message_id)] = delete_at
    logger.debug(
        f"MessageCleaner: scheduled deletion of msg {message_id} "
        f"in {delete_in_seconds:.0f}s (at ts={delete_at:.0f})"
    )


async def delete_previous_signal(user_id: int) -> None:
    """Immediately delete the last signal message for this user, if any."""
    key = _last_signal.pop(user_id, None)
    if key is None or _bot is None:
        return
    chat_id, message_id = key
    try:
        await _bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.debug(f"MessageCleaner: immediately deleted previous signal msg {message_id} for user {user_id}")
    except Exception:
        pass  # Already deleted or no permission — ignore silently
    # Remove from timed queue too if it was there
    _pending.pop((chat_id, message_id), None)


def track_signal_message(user_id: int, chat_id: int, message_id: int) -> None:
    """Remember the latest signal message for this user."""
    _last_signal[user_id] = (chat_id, message_id)


async def _cleaner_loop() -> None:
    """Runs every 30 s; deletes any messages whose time has come."""
    while True:
        await asyncio.sleep(30)
        if not _pending or _bot is None:
            continue

        now = time.time()
        expired = [(k, v) for k, v in list(_pending.items()) if v <= now]
        for (chat_id, msg_id), _ in expired:
            try:
                await _bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception:
                pass  # Already deleted or bot lacks permission — ignore silently
            _pending.pop((chat_id, msg_id), None)
            # Clean up last_signal tracker too
            for uid, (cid, mid) in list(_last_signal.items()):
                if cid == chat_id and mid == msg_id:
                    _last_signal.pop(uid, None)

        if expired:
            logger.debug(f"MessageCleaner: deleted {len(expired)} expired message(s)")


def start_cleaner(bot) -> None:
    """Start the background cleaner loop. Call after the event loop is running."""
    init_cleaner(bot)
    asyncio.create_task(_cleaner_loop())
    logger.info("✅ MessageCleaner background task started")
