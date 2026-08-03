---
name: Telegram bot startup safety
description: Keep optional Telegram API setup outside the critical startup path for the Plesk polling bot.
---

Optional Telegram setup such as publishing command menus must never be required for the bot to reach polling.

**Why:** A user-facing bot feature must not make the existing `/start` flow unavailable when Telegram API setup is delayed, unavailable, or behaves differently on Plesk.

**How to apply:** Keep command registration and similar convenience calls out of the bot startup path unless they are explicitly guarded and independently verified in the target Plesk runtime.