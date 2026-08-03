"""Anti-spam / rate limiting middleware."""
import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger


class ThrottlingMiddleware(BaseMiddleware):
    """Limits how fast each user can send requests."""

    def __init__(self, rate: float = 0.5):
        self.rate = rate  # minimum seconds between requests per user
        self._user_timestamps: Dict[int, float] = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        user_id = user.id
        now = time.monotonic()
        last = self._user_timestamps.get(user_id, 0)

        if now - last < self.rate:
            if isinstance(event, CallbackQuery):
                await event.answer("⏳ Trop vite ! Veuillez patienter.", show_alert=False)
            elif isinstance(event, Message):
                await event.answer("⏳ Trop de requêtes. Veuillez patienter un moment.")
            logger.debug(f"Throttled user {user_id}")
            return

        self._user_timestamps[user_id] = now
        return await handler(event, data)
