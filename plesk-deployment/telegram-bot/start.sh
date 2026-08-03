#!/usr/bin/env bash
set -Eeuo pipefail

BOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_ROOT"

VENV="$BOT_ROOT/.venv"
STATUS_FILE="${TELEGRAM_BOT_STATUS_FILE:-$BOT_ROOT/.bot-status.json}"
CURRENT_STAGE="boot"

select_python() {
  local candidate resolved
  local -a candidate_list=()

  if [[ -n "${BOT_PYTHON:-}" ]]; then
    candidate_list=("$BOT_PYTHON")
  else
    # Plesk can keep supported Python versions outside the normal PATH.
    # Prefer explicit Plesk/system locations before the generic python3.
    candidate_list=(
      /opt/plesk/python/*/bin/python3.12
      /opt/plesk/python/*/bin/python3.11
      /opt/plesk/python/*/bin/python3.10
      /opt/plesk/python/*/bin/python3.9
      /opt/plesk/python/*/bin/python
      /usr/local/bin/python3.12
      /usr/local/bin/python3.11
      /usr/local/bin/python3.10
      /usr/local/bin/python3.9
      /usr/bin/python3.12
      /usr/bin/python3.11
      /usr/bin/python3.10
      /usr/bin/python3.9
      python3.12
      python3.11
      python3.10
      python3.9
      python3
    )
  fi

  for candidate in "${candidate_list[@]}"; do
    # Keep unmatched globs as literal strings, then skip them below.
    [[ "$candidate" == */* && "$candidate" == *"*"* ]] && continue
    if [[ "$candidate" == */* ]]; then
      resolved="$candidate"
    else
      resolved="$(command -v "$candidate" 2>/dev/null || true)"
    fi
    [[ -n "$resolved" && -x "$resolved" ]] || continue
    if "$resolved" - <<'PY' >/dev/null 2>&1
import sys
if sys.version_info < (3, 10):
    raise SystemExit(1)
PY
    then
      PYTHON="$resolved"
      return 0
    fi
  done

  echo "Telegram bot startup: Python 3.10 or newer is required." >&2
  echo "Set BOT_PYTHON to an installed supported Python binary." >&2
  return 1
}

venv_uses_supported_python() {
  "$VENV/bin/python" - <<'PY' >/dev/null 2>&1
import sys
if sys.version_info < (3, 10):
    raise SystemExit(1)
PY
}

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

CURRENT_STAGE="select_python"
select_python

if [[ ! -x "$VENV/bin/python" ]] || ! venv_uses_supported_python; then
  if [[ -x "$VENV/bin/python" ]]; then
    echo "Telegram bot startup: replacing legacy Python virtualenv" >&2
  fi
  rm -rf "$VENV"
  CURRENT_STAGE="create_venv"
  echo "Telegram bot startup: creating Python virtualenv with $PYTHON at $VENV" >&2
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
echo "Telegram bot startup: using $("$VENV/bin/python" --version 2>&1)" >&2
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