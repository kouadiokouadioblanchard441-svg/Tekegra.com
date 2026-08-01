"""Vercel route: POST /api/webhook."""
from telegram_webhook import handler

__all__ = ["handler"]