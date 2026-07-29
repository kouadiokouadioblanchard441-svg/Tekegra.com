"""
Vercel Python serverless function — Setup unique post-déploiement.

Appelle une seule fois après le premier déploiement :
  GET https://ton-app.vercel.app/setup?token=TON_ADMIN_PASSWORD

Cela :
  1. Initialise les tables de la base de données
  2. Enregistre l'URL du webhook auprès de Telegram
"""
import asyncio
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

_BOT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'telegram-bot')
sys.path.insert(0, _BOT_ROOT)

from aiogram import Bot
from config import settings
from database.db import init_db, get_engine


async def _run_setup(webhook_url: str) -> dict:
    # 1. Initialiser les tables DB
    await init_db()

    # 2. Enregistrer le webhook Telegram
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )
    info = await bot.get_webhook_info()
    await bot.session.close()

    engine = get_engine()
    await engine.dispose()

    return {
        "webhook_url": info.url,
        "pending": info.pending_update_count,
        "last_error": info.last_error_message or "aucune",
    }


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        token = params.get("token", [""])[0]

        admin_password = os.environ.get("ADMIN_PASSWORD", "")
        if not admin_password or token != admin_password:
            self.send_response(401)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("❌ Non autorisé — passe ?token=ADMIN_PASSWORD".encode())
            return

        # Construire l'URL du webhook à partir du header Host
        host = self.headers.get("Host", "")
        webhook_url = f"https://{host}/webhook"

        try:
            result = asyncio.run(_run_setup(webhook_url))
            body = (
                f"✅ Setup terminé !\n\n"
                f"Webhook enregistré : {result['webhook_url']}\n"
                f"Updates en attente : {result['pending']}\n"
                f"Dernière erreur : {result['last_error']}"
            ).encode("utf-8")
            self.send_response(200)
        except Exception as e:
            body = f"❌ Erreur : {e}".encode("utf-8")
            self.send_response(500)

        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass
