---
name: Aiogram middleware scope
description: Middleware registration constraint for Telegram update handling.
---

Attach middleware that branches on `Message` or `CallbackQuery` to the concrete
aiogram observers (`dp.message` and `dp.callback_query`), not only to the
top-level `Update` observer.

**Why:** A top-level update middleware receives an `Update` wrapper. Type checks
for the contained event then fail, which can bypass or incorrectly block access
control before a command handler responds.

**How to apply:** Keep the database-session middleware outermost on each
concrete observer, then access-control middleware, then throttling and handlers.