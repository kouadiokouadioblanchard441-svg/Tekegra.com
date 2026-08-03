---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The production architecture uses one VPS running Plesk: Node serves the
panel/API and starts the local Python Telegram bot, with systemd as an
alternative supervisor; Replit is development-only.

**Why:** The bot needs an always-on Python process, but the user wants all
production services on the same Plesk VPS rather than on another machine.

**How to apply:** Run `dist/index.cjs` through Plesk; it starts
`telegram-bot/start.sh` with the Plesk environment. If systemd is used instead,
set `TELEGRAM_BOT_AUTOSTART=false` and configure the bot EnvironmentFile.
Keep `pip --no-user` in the virtualenv installer. The Plesk backend initializes
`bot_settings.admin_password_hash` from `ADMIN_PASSWORD` when configured.

The Node application's environment is not inherited by systemd; duplicate only
the required variables when choosing the systemd alternative.