"""Shared Vercel Telegram webhook implementation.

The public entry point is ``/api/webhook``. Telegram authenticates requests
with ``X-Telegram-Bot-Api-Secret-Token``. The handler accepts POST only,
validates the complete Update envelope, dispatches it through the existing
aiogram routers, and never logs the bot token or message contents.
"""
from __future__ import annotations

import asyncio
import hmac
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler
from typing import Any

from loguru import logger
from pydantic import ValidationError

_BOT_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "artifacts",
    "telegram-bot",
)
if _BOT_ROOT not in sys.path:
    sys.path.insert(0, _BOT_ROOT)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from bot.handlers import get_main_router
from bot.middlewares import (
    BanCheckMiddleware,
    ChannelCheckMiddleware,
    DbSessionMiddleware,
    ThrottlingMiddleware,
)
from config import settings
from database.db import init_db

MAX_BODY_BYTES = 1_000_000
_db_initialized = False

# Telegram's allowed_updates values. Keeping this list explicit prevents a
# future Bot API update type from being silently excluded at registration.
ALL_UPDATE_TYPES = [
    "message",
    "edited_message",
    "channel_post",
    "edited_channel_post",
    "business_connection",
    "business_message",
    "edited_business_message",
    "deleted_business_messages",
    "message_reaction",
    "message_reaction_count",
    "inline_query",
    "chosen_inline_result",
    "callback_query",
    "shipping_query",
    "pre_checkout_query",
    "purchased_paid_media",
    "poll",
    "poll_answer",
    "my_chat_member",
    "chat_member",
    "chat_join_request",
    "chat_boost",
    "removed_chat_boost",
]


def _update_summary(update_data: dict[str, Any]) -> dict[str, Any]:
    """Extract safe operational fields without logging message payloads."""
    update_type = next(
        (key for key in ALL_UPDATE_TYPES if key in update_data),
        "unknown",
    )
    payload = update_data.get(update_type) or {}
    if not isinstance(payload, dict):
        payload = {}
    user = payload.get("from") or payload.get("user") or {}
    chat = payload.get("chat") or {}
    text = payload.get("text") or payload.get("caption") or ""
    command = ""
    if isinstance(text, str) and text.startswith("/"):
        command = text.split(maxsplit=1)[0][:64]
    return {
        "update_id": update_data.get("update_id"),
        "update_type": update_type,
        "user_id": user.get("id"),
        "chat_id": chat.get("id"),
        "username": user.get("username"),
        "command": command,
    }


async def process_update(update_data: dict[str, Any]) -> None:
    """Dispatch one validated Telegram update through the production router."""
    global _db_initialized
    if not settings.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")

    if not _db_initialized:
        await init_db()
        _db_initialized = True
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    try:
        dispatcher = Dispatcher(storage=MemoryStorage())
        dispatcher.update.middleware(DbSessionMiddleware())
        dispatcher.update.middleware(BanCheckMiddleware())
        dispatcher.update.middleware(ChannelCheckMiddleware())
        dispatcher.update.middleware(ThrottlingMiddleware(rate=settings.THROTTLE_RATE))
        dispatcher.include_router(get_main_router())
        update = Update.model_validate(update_data)
        await dispatcher.feed_update(bot, update)
    finally:
        await bot.session.close()


def _write_response(
    request: BaseHTTPRequestHandler,
    status: int,
    body: dict[str, Any],
) -> None:
    encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request.send_response(status)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.send_header("Content-Length", str(len(encoded)))
    request.end_headers()
    request.wfile.write(encoded)


def handle_payload(
    headers: dict[str, str],
    raw_body: bytes,
    process: bool = True,
) -> tuple[int, dict[str, Any], dict[str, Any]]:
    """Validate and optionally dispatch a webhook payload.

    This small synchronous core is also used by the local verification tests.
    A valid update is processed before returning so Vercel cannot freeze an
    unawaited background thread and lose the Telegram action.
    """
    supplied_secret = headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not settings.WEBHOOK_SECRET or not hmac.compare_digest(
        supplied_secret,
        settings.WEBHOOK_SECRET,
    ):
        return 403, {"ok": False, "error": "forbidden"}, {"update_type": "unauthorized"}

    if not raw_body or len(raw_body) > MAX_BODY_BYTES:
        return 400, {"ok": False, "error": "invalid_body"}, {"update_type": "invalid"}

    try:
        update_data = json.loads(raw_body)
    except json.JSONDecodeError:
        return 400, {"ok": False, "error": "invalid_json"}, {"update_type": "invalid"}
    if not isinstance(update_data, dict) or "update_id" not in update_data:
        return 400, {"ok": False, "error": "invalid_update"}, {"update_type": "invalid"}

    try:
        Update.model_validate(update_data)
    except ValidationError:
        return 400, {"ok": False, "error": "invalid_update"}, {"update_type": "invalid"}

    summary = _update_summary(update_data)
    if process:
        asyncio.run(process_update(update_data))
    return 200, {"ok": True}, summary


class handler(BaseHTTPRequestHandler):
    """Vercel Python function for Telegram's POST webhook."""

    def do_POST(self) -> None:
        started = time.perf_counter()
        summary: dict[str, Any] = {"update_type": "unparsed"}
        status = 200
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            status, body, summary = handle_payload(
                dict(self.headers.items()),
                raw_body,
                process=True,
            )
            _write_response(self, status, body)
        except ValueError:
            status = 400
            _write_response(self, status, {"ok": False, "error": "invalid_json"})
        except Exception:
            # The update was authenticated and structurally valid. Returning
            # 200 prevents Telegram's retry storm; the full exception remains
            # in server logs and the token/payload are never exposed.
            status = 200
            logger.exception("Telegram update processing failed")
            _write_response(self, status, {"ok": False, "error": "processing_failed"})
        finally:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(
                "telegram_webhook "
                f"status={status} response_ms={elapsed_ms} "
                f"user_id={summary.get('user_id')} chat_id={summary.get('chat_id')} "
                f"username={summary.get('username')!r} "
                f"command={summary.get('command')!r} "
                f"update_type={summary.get('update_type')!r}"
            )

    def do_GET(self) -> None:
        _write_response(
            self,
            405,
            {"ok": False, "error": "method_not_allowed", "allow": "POST"},
        )

    def do_PUT(self) -> None:
        self.do_GET()

    def do_DELETE(self) -> None:
        self.do_GET()

    def log_message(self, *_args: Any) -> None:
        pass