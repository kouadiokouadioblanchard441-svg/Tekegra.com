---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The production architecture uses one VPS running Plesk: Node serves the
panel/API and a separate systemd service runs the Telegram bot; Replit is
development-only.

**Why:** The bot needs an always-on Python process, but the user wants all
production services on the same Plesk VPS rather than on another machine.

**How to apply:** Run `dist/index.cjs` through Plesk and install
`deployment/telegram-bot.service.example` on that same server. Configure the
bot's `BOT_TOKEN` and `DATABASE_URL`/`SUPABASE_DATABASE_URL` in
`/voltatrucks.online/plesk-deployment/telegram-bot/.env`. Keep `pip --no-user`
in the virtualenv installer. The Plesk backend initializes
`bot_settings.admin_password_hash` from `ADMIN_PASSWORD` when configured.

The Node application's Plesk environment is not inherited by the separate
systemd Python service; duplicate only the required runtime variables in the
bot's private EnvironmentFile.