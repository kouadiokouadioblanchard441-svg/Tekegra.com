"""
Lucky Jet AI Bot — Webhook entry point (production / Railway / Render / VPS)

Usage:
  WEBHOOK_HOST=https://your-app.railway.app python main_webhook.py

The bot registers its webhook with Telegram on startup and serves
incoming updates via an aiohttp web server.  Use this instead of
main.py (polling) when you deploy on a platform that cannot run a
persistent long-polling process (Railway, Render, Fly, VPS…).
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from loguru import logger

from config import settings
from database.db import init_db
from bot.handlers import get_main_router
from bot.middlewares import ThrottlingMiddleware, DbSessionMiddleware, BanCheckMiddleware, ChannelCheckMiddleware
from bot.utils.message_cleaner import start_cleaner

# ── Webhook configuration ────────────────────────────────────────────────────
# Set WEBHOOK_HOST to your public HTTPS domain, e.g.:
#   https://my-bot.railway.app   (Railway)
#   https://my-bot.onrender.com  (Render)
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", "").rstrip("/")
WEBHOOK_PATH = f"/webhook/{settings.TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL  = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# aiohttp will listen on 0.0.0.0:PORT  (Railway / Render inject PORT)
PORT = int(os.environ.get("PORT", "8080"))


def configure_logging():
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )


async def on_startup(bot: Bot) -> None:
    if not WEBHOOK_HOST:
        logger.error("❌ WEBHOOK_HOST is not set. Export it before starting.")
        sys.exit(1)

    await init_db()
    await bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=["message", "callback_query", "inline_query"],
        drop_pending_updates=True,
    )
    logger.info(f"✅ Webhook set → {WEBHOOK_URL}")


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("👋 Webhook deleted, bot stopped.")


def main():
    configure_logging()

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN is not set.")
        sys.exit(1)

    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(BanCheckMiddleware())
    dp.update.middleware(ChannelCheckMiddleware())
    dp.update.middleware(ThrottlingMiddleware(rate=settings.THROTTLE_RATE))
    dp.include_router(get_main_router())

    start_cleaner(bot)

    app = web.Application()
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    logger.info(f"🚀 Starting webhook server on port {PORT}…")
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
