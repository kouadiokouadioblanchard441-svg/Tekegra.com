"""Navigation helper — replaces each screen with one clean bot message."""
import asyncio

from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from loguru import logger
from bot.utils.message_cleaner import (
    delete_incoming_message,
    delete_previous_signal,
    track_signal_message,
)


async def navigate(
    call: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup,
    photo_id: str = None,
    parse_mode: str = "Markdown",
) -> None:
    """Delete the previous screen, then send exactly one replacement screen.

    Telegram animates a bot message deletion in the client. The short pause
    after delete lets that animation start before the replacement is sent.
    """
    msg = call.message
    try:
        await delete_previous_signal(call.from_user.id)
        try:
            await msg.delete()
        except Exception:
            pass
        await asyncio.sleep(0.18)
        if photo_id:
            sent = await call.bot.send_photo(
                chat_id=msg.chat.id, photo=photo_id,
                caption=text, parse_mode=parse_mode, reply_markup=keyboard,
            )
        else:
            sent = await call.bot.send_message(
                chat_id=msg.chat.id, text=text,
                parse_mode=parse_mode, reply_markup=keyboard,
            )
        track_signal_message(call.from_user.id, sent.chat.id, sent.message_id)
    except Exception as e:
        logger.warning(f"navigate() fell back to delete+resend: {e}")
        await delete_previous_signal(call.from_user.id)
        try:
            await msg.delete()
        except Exception:
            pass
        if want_photo:
            sent = await call.bot.send_photo(
                chat_id=msg.chat.id, photo=photo_id,
                caption=text, parse_mode=parse_mode, reply_markup=keyboard,
            )
        else:
            sent = await call.bot.send_message(
                chat_id=msg.chat.id, text=text,
                parse_mode=parse_mode, reply_markup=keyboard,
            )
        track_signal_message(call.from_user.id, sent.chat.id, sent.message_id)


async def send_menu(
    message: Message,
    text: str,
    keyboard: InlineKeyboardMarkup,
    photo_id: str = None,
    parse_mode: str = "Markdown",
) -> None:
    """Send a fresh menu page (used from command handlers)."""
    from bot.utils.message_cleaner import send_tracked_message, send_tracked_photo

    user_id = message.from_user.id
    await delete_incoming_message(message)
    if photo_id:
        await send_tracked_photo(
            message, user_id, photo_id, caption=text,
            parse_mode=parse_mode, reply_markup=keyboard,
        )
    else:
        await send_tracked_message(
            message, user_id, text, parse_mode=parse_mode, reply_markup=keyboard,
        )
