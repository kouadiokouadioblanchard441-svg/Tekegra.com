---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The Plesk distribution keeps the React admin panel and Express API in one Node.js process launched from the single CommonJS artifact `dist/index.cjs`, while the existing Telegram bot remains a separate Python/aiogram process. Both processes use the same PostgreSQL schema.

**Why:** Converting the bot during the hosting migration would be a high-risk rewrite and could change Telegram behavior; Plesk can supervise both services independently.

**How to apply:** Future Plesk changes should preserve same-origin `/api` routing for the Node app, keep the bot process separate, use `dist/index.cjs` as the Plesk startup file, and avoid putting secrets or `node_modules` into GitHub.

The Python bot process must receive its own `BOT_TOKEN` and
`DATABASE_URL`/`SUPABASE_DATABASE_URL`; variables configured only on the Plesk
Node application are not guaranteed to reach Supervisor/systemd.

**Why:** The bot is launched independently from Node, and its startup now
validates Telegram credentials, PostgreSQL connectivity, and polling setup
before serving updates.

**How to apply:** Configure the bot process environment separately and launch
`telegram-bot/start.sh`, which creates the virtualenv, installs pinned
dependencies, and starts `main.py`.