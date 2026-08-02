---
name: Telegram message cleanup
description: Durable rule for keeping one visible bot response and expiring it after the configured lifetime
---

All user-facing Telegram bot responses belong to one per-user message lifecycle, regardless of whether the response is sent as a new message or edited in place. The previous tracked response must be deleted before sending a replacement. Menus and access/profile screens remain until replaced; loading/signal screens use the expiry timer.

**Why:** Tracking only newly sent signal messages leaves edited menus, quota screens, and access gates orphaned in chats and allows multiple bot responses to remain visible. Telegram controls the deletion animation in the client; a short delay after deletion lets the built-in transition appear before the replacement arrives.

**How to apply:** Route command responses and fallback sends through the tracked helpers; delete all tracked IDs before replacement; call the edited-message tracker after successful `edit_text`/`edit_caption`; keep expiry scheduling only on loading/signal messages.