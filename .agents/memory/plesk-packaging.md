---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The Plesk distribution keeps the React admin panel and Express API in one Node.js process launched from the single CommonJS artifact `dist/index.cjs`, while the existing Telegram bot remains a separate Python/aiogram process. Both processes use the same PostgreSQL schema.

**Why:** Converting the bot during the hosting migration would be a high-risk rewrite and could change Telegram behavior; Plesk can supervise both services independently.

**How to apply:** Future Plesk changes should preserve same-origin `/api` routing for the Node app, keep the bot process separate, use `dist/index.cjs` as the Plesk startup file, and avoid putting secrets or `node_modules` into GitHub.

The Plesk production architecture uses one Node startup entrypoint that serves
the panel/API and starts the Telegram bot as a separate Python child process;
Replit is development-only and never hosts the bot.

**Why:** Plesk must start the full product automatically from its configured
startup file, while the bot must remain a separate Python process with aiogram.

**How to apply:** Run `dist/index.cjs` from Plesk; it starts
`telegram-bot/start.sh` with the same environment. Configure
`BOT_TOKEN` and `DATABASE_URL`/`SUPABASE_DATABASE_URL` on the Plesk Node
application. Keep `pip --no-user` in the virtualenv installer, and set
`TELEGRAM_BOT_AUTOSTART=false` only when an external Python supervisor is used.