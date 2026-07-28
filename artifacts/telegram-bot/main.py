"""
Lucky Jet AI Bot — Main entry point
Aiogram 3 + FastAPI + PostgreSQL
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config import settings
from database.db import init_db
from bot.handlers import get_main_router
from bot.middlewares import ThrottlingMiddleware, DbSessionMiddleware, BanCheckMiddleware, ChannelCheckMiddleware
from bot.utils.message_cleaner import start_cleaner


def configure_logging():
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    logger.add(
        "logs/bot.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="DEBUG",
        encoding="utf-8",
    )


async def main():
    configure_logging()

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN is not set! Add it to your environment secrets.")
        sys.exit(1)

    logger.info(f"🚀 Starting {settings.BOT_NAME}...")

    # Initialize database — required; fail fast if unavailable
    try:
        await init_db()
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error("Bot cannot start without a database. Check DATABASE_URL.")
        sys.exit(1)

    # Create bot and dispatcher
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middlewares (order matters):
    # 1. DB session injected first so later middlewares can use it
    # 2. Ban check — blocks banned/rejected/pending users
    # 3. Channel check — blocks users who haven't joined required channels
    # 4. Throttling last, applied only to legitimate users
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(BanCheckMiddleware())
    dp.update.middleware(ChannelCheckMiddleware())
    dp.update.middleware(ThrottlingMiddleware(rate=settings.THROTTLE_RATE))

    # Include all routers
    dp.include_router(get_main_router())

    # Start background task — auto-deletes signal messages after game time + 2 min
    start_cleaner(bot)

    # Start polling
    logger.info("✅ Bot is running. Press Ctrl+C to stop.")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
    finally:
        await bot.session.close()
        logger.info("👋 Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
