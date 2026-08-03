---
name: Plesk Python runtime
description: Plesk may retain a legacy Telegram-bot virtualenv created with an unsupported Python interpreter.
---

The Telegram bot requires Python 3.10 or newer. A Plesk `.venv` created with an older interpreter can fail before `main()` with `SyntaxError: future feature annotations is not defined`, so database state and Telegram handlers are never reached.

**Why:** Plesk can preserve the virtualenv across Git pulls and application restarts; updating `start.sh` alone does not repair an already-created environment unless the startup path validates and recreates it.

**How to apply:** Keep startup detection for Python 3.10+ and rebuild the virtualenv when its interpreter is too old. Confirm the deployed commit and health status after Pull → Deploy Now → Restart App.