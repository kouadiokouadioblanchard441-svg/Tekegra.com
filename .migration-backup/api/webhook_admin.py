"""Protected webhook management operations for Vercel.

POST /api/webhook/setup
POST /api/webhook/info
POST /api/webhook/delete

Both the admin ID and the webhook secret are required. No token is ever
included in a response or log.
"""
from __future__ import annotations

import asyncio
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import parse_qs, urlparse

from aiogram import Bot

_BOT_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "artifacts",
    "telegram-bot",
)
if _BOT_ROOT not in sys.path:
    sys.path.insert(0, _BOT_ROOT)

from config import settings
from telegram_webhook import ALL_UPDATE_TYPES


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


def _state(info) -> str:
    if not info.url:
        return "not_configured"
    if info.last_error_message:
        return "error"
    if info.pending_update_count:
        return "active_with_pending_updates"
    return "active"


async def _telegram_action(action: str) -> dict[str, Any]:
    if not settings.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        if action == "setup":
            app_url = settings.APP_URL.rstrip("/")
            if not app_url.startswith("https://"):
                raise ValueError("APP_URL must be an HTTPS Vercel URL")
            webhook_url = f"{app_url}/api/webhook"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=settings.WEBHOOK_SECRET,
                # Telegram interprets [] as all update types, including new
                # Bot API types added after this code was deployed.
                allowed_updates=[],
                drop_pending_updates=False,
            )
        elif action == "delete":
            await bot.delete_webhook(drop_pending_updates=False)
        info = await bot.get_webhook_info()
        return {
            "ok": True,
            "state": _state(info),
            "url": info.url,
            "pending_update_count": info.pending_update_count,
            "last_error_message": info.last_error_message,
            "last_error_date": info.last_error_date,
            "ip_address": info.ip_address,
            "max_connections": info.max_connections,
            "action": action,
        }
    finally:
        await bot.session.close()


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        admin_id = self.headers.get("X-Admin-ID", "")
        authorization = self.headers.get("Authorization", "")
        expected_auth = f"Bearer {settings.WEBHOOK_SECRET}"
        if (
            not settings.ADMIN_ID
            or not hmac.compare_digest(admin_id, settings.ADMIN_ID)
            or not settings.WEBHOOK_SECRET
            or not hmac.compare_digest(authorization, expected_auth)
        ):
            _write_response(self, 403, {"ok": False, "error": "forbidden"})
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query_action = parse_qs(parsed.query).get("action", [""])[0]
        action = {
            "/api/webhook/setup": "setup",
            "/api/webhook/info": "info",
            "/api/webhook/delete": "delete",
            "/api/webhook_admin": "info",
        }.get(path, query_action)
        if not action:
            _write_response(self, 404, {"ok": False, "error": "unknown_action"})
            return
        try:
            _write_response(self, 200, asyncio.run(_telegram_action(action)))
        except Exception:
            _write_response(self, 500, {"ok": False, "error": "telegram_api_error"})

    def do_GET(self) -> None:
        _write_response(
            self,
            405,
            {"ok": False, "error": "method_not_allowed", "allow": "POST"},
        )

    def log_message(self, *_args: Any) -> None:
        pass