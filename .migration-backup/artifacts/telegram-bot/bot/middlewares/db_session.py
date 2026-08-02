"""Inject async DB session into handler data."""
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.db import get_session_factory


class DbSessionMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        factory = get_session_factory()
        async with factory() as session:
            data["session"] = session
            return await handler(event, data)
