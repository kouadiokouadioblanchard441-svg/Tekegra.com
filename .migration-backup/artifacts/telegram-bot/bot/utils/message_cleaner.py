"""Keeps one visible bot message per user and replaces it cleanly.

Rules:
  • the latest bot response is automatically deleted after 600 seconds.
  • when a new response is sent, the previous tracked response is removed first.
  • every tracked response belongs to the same per-user lifecycle.
"""
import asyncio
import time
from loguru import logger

# {(chat_id, message_id): delete_at_unix_timestamp}
_pending: dict[tuple[int, int], float] = {}

# Last bot message per user: {user_id: (chat_id, message_id)}
_last_signal: dict[int, tuple[int, int]] = {}
# Safety net for messages tracked during quick consecutive callbacks. Normally
# this contains one item, but keeping all IDs lets cleanup remove an orphaned
# response instead of leaving two bot messages in the chat.
_tracked_messages: dict[int, set[tuple[int, int]]] = {}

_bot = None
SIGNAL_TTL_SECONDS = 10 * 60
# Telegram animates an actual delete in the client. Keep only a tiny buffer;
# a longer sleep makes every navigation feel slow.
DELETE_ANIMATION_DELAY_SECONDS = 0.04


def init_cleaner(bot) -> None:
    """Call once at startup to attach the bot instance."""
    global _bot
    _bot = bot


async def delete_previous_signal(user_id: int) -> None:
    """Delete every tracked bot response for this user before replacing it."""
    keys = set(_tracked_messages.pop(user_id, set()))
    last = _last_signal.pop(user_id, None)
    if last is not None:
        keys.add(last)
    if not keys or _bot is None:
        return
    deleted_any = False
    for chat_id, message_id in keys:
        try:
            await _bot.delete_message(chat_id=chat_id, message_id=message_id)
            deleted_any = True
            logger.debug(
                f"MessageCleaner: deleted previous bot msg {message_id} for user {user_id}"
            )
        except Exception:
            pass  # Already deleted or bot lacks permission — ignore silently
        _pending.pop((chat_id, message_id), None)
    if deleted_any:
        # Telegram performs the visual deletion animation in the client. A
        # small gap prevents the replacement from arriving in the same frame.
        await asyncio.sleep(DELETE_ANIMATION_DELAY_SECONDS)


async def delete_incoming_message(message) -> None:
    """Remove a user's command/message when Telegram allows it."""
    try:
        await message.delete()
    except Exception:
        pass


def schedule_delete(chat_id: int, message_id: int, delete_in_seconds: float = SIGNAL_TTL_SECONDS) -> None:
    """Schedule a signal message for deletion after the configured TTL."""
    _pending[(chat_id, message_id)] = time.time() + delete_in_seconds


def track_signal_message(user_id: int, chat_id: int, message_id: int) -> None:
    """Remember the latest bot message for this user."""
    key = (chat_id, message_id)
    _last_signal[user_id] = key
    _tracked_messages.setdefault(user_id, set()).add(key)


def is_tracked_message(user_id: int, message) -> bool:
    """Return whether a message is already part of this user's lifecycle."""
    key = (message.chat.id, message.message_id)
    return key in _tracked_messages.get(user_id, set())


async def track_existing_message(user_id: int, message) -> None:
    """Track a message that was edited in place.

    If another response was tracked for this user, remove it first. This
    prevents a fallback/new message from remaining beside an edited screen.
    """
    key = (message.chat.id, message.message_id)
    # An edited screen becomes the sole current response. Remove any response
    # left by a rapid callback or a failed send, but keep this edited message.
    old_keys = _tracked_messages.get(user_id, set()).copy()
    deleted_any = False
    for old_chat_id, old_message_id in old_keys:
        if (old_chat_id, old_message_id) == key:
            continue
        try:
            await _bot.delete_message(
                chat_id=old_chat_id,
                message_id=old_message_id,
            )
            deleted_any = True
        except Exception:
            pass
        _pending.pop((old_chat_id, old_message_id), None)
    _tracked_messages[user_id] = {key}
    _last_signal[user_id] = key
    # Edited menus and profile/access screens are persistent. If this message
    # used to be a signal, cancel its old expiry now that it is a menu screen.
    _pending.pop(key, None)
    if deleted_any:
        await asyncio.sleep(DELETE_ANIMATION_DELAY_SECONDS)


async def send_tracked_message(message, user_id: int, text: str, **kwargs):
    """Delete the previous response, send one text response, and track it."""
    await delete_previous_signal(user_id)
    sent = await message.answer(text, **kwargs)
    track_signal_message(user_id, sent.chat.id, sent.message_id)
    return sent


async def send_tracked_photo(message, user_id: int, photo: str, **kwargs):
    """Delete the previous response, send one photo response, and track it."""
    await delete_previous_signal(user_id)
    sent = await message.answer_photo(photo=photo, **kwargs)
    track_signal_message(user_id, sent.chat.id, sent.message_id)
    return sent


def clear_signal_tracking(user_id: int) -> None:
    """Clear the tracking for a user without deleting the message.

    Use this when the user navigates away from a signal (e.g. back to menu)
    and the signal message has been transformed in-place into a menu message.
    """
    _last_signal.pop(user_id, None)
    _tracked_messages.pop(user_id, None)


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
                    _tracked_messages.pop(user_id, None)


def start_cleaner(bot) -> None:
    """Attach the bot instance and start the expiry loop."""
    init_cleaner(bot)
    asyncio.create_task(_cleaner_loop())
    logger.info("✅ MessageCleaner started (signals expire after 10 minutes)")
