---
name: Vercel serverless bot limits
description: Runtime constraints to account for when publishing the Telegram bot through Vercel Functions
---

Vercel Functions are stateless and do not guarantee a persistent Python process or background asyncio task between Telegram webhook requests. In-memory message tracking and delayed cleanup are reliable in the long-running polling workflow, but need a persistent store plus an external scheduler for equivalent production behavior on Vercel.

**Why:** The bot's ten-minute signal expiry and immediate replacement logic depend on process memory and a background cleaner.

**How to apply:** Treat Vercel webhook publishing as request handling only; use a continuously running VM/service when timed background behavior must be guaranteed, or move tracking/cleanup to durable storage and scheduled invocations.