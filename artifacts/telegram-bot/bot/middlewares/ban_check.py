"""Middleware that blocks banned, rejected, and pending users."""
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from database.models import User
from loguru import logger


class BanCheckMiddleware(BaseMiddleware):
    """Gate keeper — blocks banned/rejected users, pauses pending ones.

    Passes /start through without gating so that:
      • New users can be created and see the "pending" message.
      • Pending/rejected users can re-check their status anytime.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Let /start through for non-banned users so:
        # • new users get created and see the pending message
        # • pending/rejected users can re-check their status
        # Banned users are NOT bypassed here — ban_check below will catch them
        # AND start.py also explicitly checks is_banned for /start.
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)

        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        session = data.get("session")
        if session is None:
            return await handler(event, data)

        result = await session.execute(
            select(User.is_banned, User.approval_status)
            .where(User.telegram_id == user.id)
        )
        row = result.one_or_none()

        # Unknown user — let handler create them via get_or_create
        if row is None:
            return await handler(event, data)

        is_banned, approval_status = row

        # Note: banned users are blocked even on /start (start.py re-checks is_banned)
        if is_banned:
            logger.debug(f"Blocked banned user {user.id}")
            msg = "🚫 Votre compte est banni."
            if isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(msg)
            return

        if approval_status == "rejected":
            logger.debug(f"Blocked rejected user {user.id}")
            msg = "🚫 Votre accès au bot a été refusé."
            if isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(msg)
            return

        if approval_status == "pending":
            logger.debug(f"Blocked pending user {user.id}")
            msg = "⏳ Votre compte est en attente d'approbation par un admin."
            if isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(
                    f"⏳ *Accès en attente*\n\n"
                    f"Votre demande est en cours de traitement.\n"
                    f"Un admin va l'examiner sous peu.\n\n"
                    f"🎁 Code promo 1WIN : *{__import__('config').settings.BOT_PROMO_CODE}*",
                    parse_mode="Markdown",
                )
            return

        return await handler(event, data)
