"""
Vercel Python serverless function — Telegram webhook handler.

Telegram envoie un POST avec l'Update JSON à chaque message/callback.
On le traite avec aiogram et on répond 200 OK.
"""
import asyncio
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Rendre le code du bot importable
_BOT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'telegram-bot')
sys.path.insert(0, _BOT_ROOT)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from loguru import logger

from config import settings
from database.db import init_db, get_engine
from bot.handlers import get_main_router
from bot.middlewares import (
    ThrottlingMiddleware,
    DbSessionMiddleware,
    BanCheckMiddleware,
    ChannelCheckMiddleware,
)


async def _process_update(update_data: dict) -> None:
    """Traite un seul Update Telegram de manière serverless-safe."""
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Middlewares — même ordre que main.py
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(BanCheckMiddleware())
    dp.update.middleware(ChannelCheckMiddleware())
    dp.update.middleware(ThrottlingMiddleware(rate=0.3))
    dp.include_router(get_main_router())

    # Init tables (idempotent — très rapide si déjà existantes)
    await init_db()

    update = Update.model_validate(update_data)
    await dp.feed_update(bot, update)

    await bot.session.close()
    # Libérer les connexions DB (NullPool — déjà fermées après chaque transaction)
    engine = get_engine()
    await engine.dispose()


class handler(BaseHTTPRequestHandler):
    """Handler Vercel Python (BaseHTTPRequestHandler)."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            update_data = json.loads(body)
            asyncio.run(_process_update(update_data))
        except Exception as e:
            logger.error(f"Webhook error: {e}")
        # Toujours répondre 200 — Telegram retry sinon
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Lucky Jet Bot - Webhook actif")

    def log_message(self, *args):
        pass  # Silence les logs d'accès HTTP
