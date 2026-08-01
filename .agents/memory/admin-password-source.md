---
name: Admin password source
description: The admin panel password is managed in Supabase rather than deployment environment variables.
---

The admin panel must use `bot_settings.admin_password_hash` in Supabase as its only password authority. Deployment variables should not provide an alternate password or a default.

**Why:** A deployment password and a database password could silently diverge, causing valid credentials to be rejected after redeployments.

**How to apply:** Keep `SESSION_SECRET` for signing admin sessions, but do not reintroduce `ADMIN_PASSWORD` as a login fallback or startup seed. Change the password through the authenticated admin settings flow or update the Supabase hash through the project’s controlled setup.