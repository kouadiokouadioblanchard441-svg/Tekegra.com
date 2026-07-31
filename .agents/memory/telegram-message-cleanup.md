---
name: Telegram message cleanup
description: Durable rule for keeping one visible bot response and expiring it after the configured lifetime
---

All user-facing Telegram bot responses belong to one per-user message lifecycle, regardless of whether the response is sent as a new message or edited in place. The previous tracked response must be deleted before sending a replacement, and edited responses must be tracked for automatic expiry.

**Why:** Tracking only newly sent signal messages leaves edited menus, quota screens, and access gates orphaned in chats and allows multiple bot responses to remain visible.

**How to apply:** Route command responses and fallback sends through the tracked helpers; call the edited-message tracker after successful `edit_text`/`edit_caption`; keep the expiry loop aligned with the lifecycle TTL.