---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The Plesk distribution keeps the React admin panel and Express API in one Node.js process launched from the single CommonJS artifact `dist/index.cjs`, while the existing Telegram bot remains a separate Python/aiogram process. Both processes use the same PostgreSQL schema.

**Why:** Converting the bot during the hosting migration would be a high-risk rewrite and could change Telegram behavior; Plesk can supervise both services independently.

**How to apply:** Future Plesk changes should preserve same-origin `/api` routing for the Node app, keep the bot process separate, use `dist/index.cjs` as the Plesk startup file, and avoid putting secrets or `node_modules` into GitHub.

The default Plesk startup launches the Python bot as a child process of
`dist/index.cjs`, so it inherits the Node application's environment; a separate
Supervisor bot must be disabled or use `TELEGRAM_BOT_AUTOSTART=false`.

**Why:** Variables configured for Plesk's Node application are not guaranteed to
reach an independently configured Supervisor process, and two Telegram polling
processes cause a conflict.

**How to apply:** Keep `BOT_TOKEN` and `DATABASE_URL`/`SUPABASE_DATABASE_URL` on
the Plesk Node application, and let `telegram-bot/start.sh` create its
virtualenv and start `main.py`. The launcher must use `pip --no-user`.