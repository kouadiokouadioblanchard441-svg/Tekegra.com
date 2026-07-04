"""Middleware that blocks banned users from interacting with the bot."""
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from database.models import User
from loguru import logger


class BanCheckMiddleware(BaseMiddleware):
    """Silently ignore updates from banned users."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        session = data.get("session")
        if session is None:
            return await handler(event, data)

        result = await session.execute(
            select(User.is_banned).where(User.telegram_id == user.id)
        )
        row = result.scalar_one_or_none()
        if row is True:
            logger.debug(f"Blocked banned user {user.id}")
            if isinstance(event, CallbackQuery):
                await event.answer("🚫 Votre compte est banni.", show_alert=True)
            elif isinstance(event, Message):
                await event.answer("🚫 Votre compte est banni.")
            return  # drop the update

        return await handler(event, data)
