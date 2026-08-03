"""Long-polling entrypoint for the Telegram bot.

The bot runs as a persistent process under the hosting provider's process
manager. Long polling avoids the need for a public webhook endpoint.
"""
from __future__ import annotations

import asyncio
import sys
import os

# Ensure the telegram-bot directory is on sys.path so all internal imports work.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

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
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Configure it in the process environment.")
        sys.exit(1)

    logger.info("Initialising database…")
    await init_db()

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    await bot.set_my_commands([
        BotCommand(command="start", description="Démarrer le bot"),
        BotCommand(command="menu", description="Ouvrir le menu principal"),
        BotCommand(command="profile", description="Voir mon profil"),
        BotCommand(command="premium", description="Ouvrir Premium"),
        BotCommand(command="language", description="Changer de langue"),
        BotCommand(command="help", description="Afficher l'aide"),
    ])
    logger.info("Telegram bot commands published")

    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(BanCheckMiddleware())
    dp.update.middleware(ChannelCheckMiddleware())
    dp.update.middleware(ThrottlingMiddleware(rate=settings.THROTTLE_RATE))
    dp.include_router(get_main_router())

    # Drop any updates that arrived while the bot was offline so we don't
    # replay stale messages on startup.
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info(f"Starting polling — bot: {settings.BOT_NAME}")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
