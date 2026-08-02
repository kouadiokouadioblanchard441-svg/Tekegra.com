---
name: Telegram bot performance
description: Keep callback interactions responsive by avoiding unnecessary network round trips and artificial sleeps
---

Button callbacks should answer quickly and avoid repeated Supabase/Telegram requests. Same-type screens should be edited in place; delete-and-resend is only needed when switching between photo and text. Cache channel configuration briefly, cache membership checks for a few seconds, and do not commit user activity on every callback.

**Why:** The bot felt slow because navigation performed delete plus send, callbacks repeated channel/settings queries, and artificial analysis/deletion delays accumulated before Telegram received the callback answer.

**How to apply:** Preserve the short loading state only for signal generation, keep artificial sleeps minimal, and measure new latency changes against both Telegram API calls and Supabase writes.