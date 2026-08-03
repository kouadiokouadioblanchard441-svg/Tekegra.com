#!/usr/bin/env bash
set -Eeuo pipefail

BOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_ROOT"

PYTHON="${BOT_PYTHON:-python3}"
VENV="$BOT_ROOT/.venv"
STATUS_FILE="${TELEGRAM_BOT_STATUS_FILE:-$BOT_ROOT/.bot-status.json}"
CURRENT_STAGE="boot"

write_shell_status() {
  local status="$1"
  local stage="$2"
  local code="${3:-}"
  local timestamp
  local temporary

  timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  temporary="${STATUS_FILE}.$$"
  if [[ -n "$code" ]]; then
    printf '{"status":"%s","pid":%s,"stage":"%s","exitCode":%s,"at":"%s"}\n' \
      "$status" "$$" "$stage" "$code" "$timestamp" > "$temporary" &&
      mv -f "$temporary" "$STATUS_FILE"
  else
    printf '{"status":"%s","pid":%s,"stage":"%s","at":"%s"}\n' \
      "$status" "$$" "$stage" "$timestamp" > "$temporary" &&
      mv -f "$temporary" "$STATUS_FILE"
  fi
  # Diagnostics must never prevent the bot itself from starting.
  rm -f "$temporary" 2>/dev/null || true
  return 0
}

on_start_failure() {
  local code=$?
  write_shell_status "failed" "$CURRENT_STAGE" "$code" || true
  exit "$code"
}

trap on_start_failure ERR
write_shell_status "starting" "$CURRENT_STAGE" || true

if [[ ! -x "$VENV/bin/python" ]]; then
  CURRENT_STAGE="create_venv"
  echo "Telegram bot startup: creating Python virtualenv at $VENV" >&2
  "$PYTHON" -m venv "$VENV"
fi

# Do not run pip on every Plesk restart. Passenger environments may block
# network/package-manager operations even though the already-installed
# virtualenv is healthy. Install only when an application import is missing.
CURRENT_STAGE="check_dependencies"
if ! "$VENV/bin/python" - <<'PY'
import aiofiles
import aiohttp
import aiogram
import asyncpg
import babel
import fastapi
import httpx
import loguru
import PIL
import pydantic_settings
import sqlalchemy
import starlette
import uvicorn
PY
then
  CURRENT_STAGE="install_requirements"
  echo "Telegram bot startup: installing Python requirements" >&2
  "$VENV/bin/python" -m pip install \
    --no-user \
    --disable-pip-version-check \
    --no-input \
    --no-cache-dir \
    -r "$BOT_ROOT/requirements.txt"
fi

# Validate the configuration before starting polling. The Python systemd
# service does not inherit the environment of the separate Plesk Node.js app,
# so BOT_TOKEN and the database URL must be provided by systemd's
# EnvironmentFile or this package's private .env file.
# Keep the values themselves out of logs; only report missing variable names.
CURRENT_STAGE="validate_configuration"
echo "Telegram bot startup: validating configuration" >&2
"$VENV/bin/python" - <<'PY'
from config import settings

missing = []
if not settings.BOT_TOKEN.strip():
    missing.append("BOT_TOKEN")
if not settings.effective_database_url.strip():
    missing.append("DATABASE_URL or SUPABASE_DATABASE_URL")

if missing:
    raise SystemExit(
        "Telegram bot configuration is incomplete. "
        "Missing: " + ", ".join(missing) +
        ". Configure these variables in "
        "/voltatrucks.online/plesk-deployment/telegram-bot/.env or systemd."
    )
PY

CURRENT_STAGE="launch_python"
write_shell_status "launching" "$CURRENT_STAGE" || true
echo "Telegram bot startup: launching main.py" >&2
exec "$VENV/bin/python" "$BOT_ROOT/main.py"