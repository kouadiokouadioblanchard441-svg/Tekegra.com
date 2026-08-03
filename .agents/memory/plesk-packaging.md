---
name: Plesk packaging
description: Durable deployment decision for the standalone Plesk distribution.
---

The Plesk distribution keeps the React admin panel and Express API in one Node.js process, while the existing Telegram bot remains a separate Python/aiogram process. Both processes use the same PostgreSQL schema.

**Why:** Converting the bot during the hosting migration would be a high-risk rewrite and could change Telegram behavior; Plesk can supervise both services independently.

**How to apply:** Future Plesk changes should preserve same-origin `/api` routing for the Node app, keep the bot process separate, and avoid putting secrets or `node_modules` into the distribution archive.