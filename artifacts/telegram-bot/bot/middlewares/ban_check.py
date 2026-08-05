"""Middleware that blocks banned users."""
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from database.models import User
from loguru import logger


class BanCheckMiddleware(BaseMiddleware):
    """Gate keeper — blocks banned users only. No approval required."""

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
        row = result.one_or_none()

        # Unknown user — let handler create them via get_or_create
        if row is None:
            return await handler(event, data)

        (is_banned,) = row

        if is_banned:
            logger.debug(f"Blocked banned user {user.id}")
            msg = "🚫 Votre compte est banni."
            if isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(msg)
            return

        return await handler(event, data)
