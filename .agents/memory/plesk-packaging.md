---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The production architecture uses Plesk for the Node panel/API and a separate
VPS systemd service for the Telegram bot; Replit is development-only.

**Why:** The bot needs an always-on Python host and must not depend on the Plesk
Node process or the Replit workspace.

**How to apply:** Run `dist/index.cjs` only on Plesk and
install `deployment/telegram-bot.service.example` on the VPS. Configure the
bot's `BOT_TOKEN` and `DATABASE_URL`/`SUPABASE_DATABASE_URL` in the VPS `.env`.
Keep `pip --no-user` in the virtualenv installer. The Plesk backend initializes
`bot_settings.admin_password_hash` from `ADMIN_PASSWORD` when configured.