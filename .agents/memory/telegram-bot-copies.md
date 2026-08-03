---
name: Telegram bot copies
description: Deployment caution for duplicated Telegram bot source trees.
---

The repository contains both a Plesk production bot tree and a legacy artifact bot tree. User-facing keyboard changes must be synchronized in both until the legacy copy is removed or the deployment path is formally changed.

**Why:** The two trees had different Lucky Jet Premium menus, so the visible commands depended on which supervisor/path was running.

**How to apply:** Treat `plesk-deployment/telegram-bot/` as the production source, but mirror changes to `artifacts/telegram-bot/` when its copy can still be started by an existing deployment.