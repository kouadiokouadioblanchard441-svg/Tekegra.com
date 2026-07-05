"""Navigation helper — handles photo ↔ text transitions cleanly."""
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from loguru import logger


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
        elif not is_photo and not want_photo:
            await msg.edit_text(text, parse_mode=parse_mode, reply_markup=keyboard)
        else:
            # Switch type — delete and resend
            await msg.delete()
            if want_photo:
                await call.bot.send_photo(
                    chat_id=msg.chat.id, photo=photo_id,
                    caption=text, parse_mode=parse_mode, reply_markup=keyboard,
                )
            else:
                await call.bot.send_message(
                    chat_id=msg.chat.id, text=text,
                    parse_mode=parse_mode, reply_markup=keyboard,
                )
    except Exception as e:
        logger.warning(f"navigate() fell back to delete+resend: {e}")
        try:
            await msg.delete()
        except Exception:
            pass
        if want_photo:
            await call.bot.send_photo(
                chat_id=msg.chat.id, photo=photo_id,
                caption=text, parse_mode=parse_mode, reply_markup=keyboard,
            )
        else:
            await call.bot.send_message(
                chat_id=msg.chat.id, text=text,
                parse_mode=parse_mode, reply_markup=keyboard,
            )


async def send_menu(
    message: Message,
    text: str,
    keyboard: InlineKeyboardMarkup,
    photo_id: str = None,
    parse_mode: str = "Markdown",
) -> None:
    """Send a fresh menu page (used from command handlers)."""
    if photo_id:
        await message.answer_photo(
            photo=photo_id, caption=text,
            parse_mode=parse_mode, reply_markup=keyboard,
        )
    else:
        await message.answer(text, parse_mode=parse_mode, reply_markup=keyboard)
