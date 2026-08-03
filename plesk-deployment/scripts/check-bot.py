"""Build-time verification for the standalone Telegram bot."""

from __future__ import annotations

import compileall
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOT_ROOT = ROOT / "telegram-bot"

if not compileall.compile_dir(str(BOT_ROOT), quiet=1, maxlevels=20):
    raise SystemExit("Telegram bot Python compilation failed.")

sys.path.insert(0, str(BOT_ROOT))

# Import every application module without starting polling or contacting
# Telegram/PostgreSQL. This catches missing packages and broken imports during
# the GitHub build instead of after Plesk has restarted the application.
import main  # noqa: E402,F401

print("Telegram bot Python compilation and imports passed.")