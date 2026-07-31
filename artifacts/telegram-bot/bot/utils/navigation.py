"""Navigation helper — handles photo ↔ text transitions cleanly."""
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from loguru import logger
from bot.utils.message_cleaner import (
    delete_incoming_message,
    delete_previous_signal,
    track_existing_message,
    track_signal_message,
    schedule_delete,
)


async def navigate(
    call: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup,
    photo_id: str = None,
    parse_mode: str = "Markdown",
) -> None:
    """Navigate to a page, handling photo/text message type switching."""
    msg = call.message
    is_photo = bool(msg.photo)
    want_photo = bool(photo_id)

    try:
        if is_photo and want_photo:
            await msg.edit_caption(caption=text, parse_mode=parse_mode, reply_markup=keyboard)
            await track_existing_message(call.from_user.id, msg)
        elif not is_photo and not want_photo:
            await msg.edit_text(text, parse_mode=parse_mode, reply_markup=keyboard)
            await track_existing_message(call.from_user.id, msg)
        else:
            # Switch type — delete and resend
            await delete_previous_signal(call.from_user.id)
            await msg.delete()
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
            schedule_delete(sent.chat.id, sent.message_id)
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
        schedule_delete(sent.chat.id, sent.message_id)


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
