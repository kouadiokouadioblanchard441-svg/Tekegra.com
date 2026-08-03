"""Plesk entrypoint — runs the bot in long-polling mode.

The bot is intentionally a separate process from the Node.js admin server.
Long polling is suitable for a Plesk process manager and requires no public
webhook endpoint.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

# Ensure the telegram-bot directory is on sys.path so all internal imports work.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


STATUS_FILE = os.environ.get(
    "TELEGRAM_BOT_STATUS_FILE",
    os.path.join(_HERE, ".bot-status.json"),
)


def _write_status(status: str, **details) -> None:
    """Publish a secret-free status file for the parent Plesk process."""
    payload = {
        "status": status,
        "pid": os.getpid(),
        "at": datetime.now(timezone.utc).isoformat(),
        **details,
    }
    try:
        directory = os.path.dirname(STATUS_FILE) or "."
        fd, temporary = tempfile.mkstemp(
            prefix=".bot-status.",
            suffix=".tmp",
            dir=directory,
            text=True,
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        os.replace(temporary, STATUS_FILE)
    except Exception as error:
        # Status reporting must never prevent the bot from starting.
        logger.warning(f"Could not write bot status: {error}")


from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import get_main_router
from bot.middlewares import (
    BanCheckMiddleware,
    ChannelCheckMiddleware,
    DbSessionMiddleware,
    ThrottlingMiddleware,
)
from config import settings
from database.db import init_db


async def main() -> None:
    _write_status("starting")
    if not settings.BOT_TOKEN:
        _write_status("failed", error="BOT_TOKEN is not configured")
        logger.error("BOT_TOKEN is not set in the bot process environment.")
        sys.exit(1)

    if not settings.effective_database_url:
        _write_status(
            "failed",
            error="DATABASE_URL or SUPABASE_DATABASE_URL is not configured",
        )
        logger.error(
            "DATABASE_URL or SUPABASE_DATABASE_URL is not set in the bot process environment."
        )
        sys.exit(1)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    try:
        bot_info = await bot.get_me()
        _write_status(
            "telegram_verified",
            botId=bot_info.id,
            botUsername=bot_info.username,
            botName=bot_info.first_name,
        )
        logger.info(f"Telegram connection verified for @{bot_info.username}")

        logger.info("Initialising database…")
        await init_db()
        _write_status(
            "database_ready",
            botId=bot_info.id,
            botUsername=bot_info.username,
            botName=bot_info.first_name,
        )

        dp = Dispatcher(storage=MemoryStorage())
        # Register middleware on the concrete Telegram event observers.
        #
        # `dp.update.middleware(...)` receives an aiogram Update object, not
        # the contained Message/CallbackQuery.  The access-control middleware
        # intentionally checks those concrete event types; registering it on
        # Update could therefore silently block /start without being able to
        # answer the user.  The DB session must be outermost so it is
        # available to the access-control middleware and to every handler.
        for observer in (dp.message, dp.callback_query):
            observer.outer_middleware(DbSessionMiddleware())
            observer.outer_middleware(BanCheckMiddleware())
            observer.outer_middleware(ChannelCheckMiddleware())
            observer.middleware(ThrottlingMiddleware(rate=settings.THROTTLE_RATE))
        dp.include_router(get_main_router())

        # Drop any updates that arrived while the bot was offline so we don't
        # replay stale messages on startup.
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Starting polling — bot: %s", settings.BOT_NAME)
        _write_status(
            "polling",
            botId=bot_info.id,
            botUsername=bot_info.username,
            botName=bot_info.first_name,
        )
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as error:
        _write_status(
            "failed",
            error=f"{type(error).__name__}: {error}"[:500],
        )
        logger.exception("Telegram bot failed before or during polling")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
