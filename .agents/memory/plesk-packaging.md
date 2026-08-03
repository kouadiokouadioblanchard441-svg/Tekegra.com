---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The Plesk distribution keeps the React admin panel and Express API in one Node.js process launched from the single CommonJS artifact `dist/index.cjs`, while the existing Telegram bot remains a separate Python/aiogram process. Both processes use the same PostgreSQL schema.

**Why:** Converting the bot during the hosting migration would be a high-risk rewrite and could change Telegram behavior; Plesk can supervise both services independently.

**How to apply:** Future Plesk changes should preserve same-origin `/api` routing for the Node app, keep the bot process separate, use `dist/index.cjs` as the Plesk startup file, and avoid putting secrets or `node_modules` into GitHub.

The Plesk production architecture keeps Node.js and the Telegram bot as
independent services; Replit is development-only and never hosts the bot.

**Why:** The bot must remain operational on the user's Plesk server even when
the Replit workspace is stopped, and the Python process has its own environment.

**How to apply:** Run `dist/index.cjs` only for Node.js and run
`telegram-bot/start.sh` under Supervisor/systemd as Python. Configure
`BOT_TOKEN` and `DATABASE_URL`/`SUPABASE_DATABASE_URL` in the Python service.
Keep the `pip --no-user` virtualenv installation.