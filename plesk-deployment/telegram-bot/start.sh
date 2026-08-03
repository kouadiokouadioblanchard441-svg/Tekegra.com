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
      "$status" "$$" "$stage" "$code" "$timestamp" > "$temporary"
  else
    printf '{"status":"%s","pid":%s,"stage":"%s","at":"%s"}\n' \
      "$status" "$$" "$stage" "$timestamp" > "$temporary"
  fi
  mv -f "$temporary" "$STATUS_FILE"
}

on_start_failure() {
  local code=$?
  write_shell_status "failed" "$CURRENT_STAGE" "$code" || true
  exit "$code"
}

trap on_start_failure ERR
write_shell_status "starting" "$CURRENT_STAGE"

if [[ ! -x "$VENV/bin/python" ]]; then
  CURRENT_STAGE="create_venv"
  "$PYTHON" -m venv "$VENV"
fi

# Some hosting environments set PIP_USER globally. That is incompatible with
# a virtualenv ("user site-packages are not visible in this virtualenv"), so
# explicitly keep both pip operations inside the bot virtualenv.
CURRENT_STAGE="upgrade_pip"
"$VENV/bin/python" -m pip install --no-user --quiet --upgrade pip
CURRENT_STAGE="install_requirements"
"$VENV/bin/python" -m pip install --no-user --quiet -r "$BOT_ROOT/requirements.txt"

# Validate the configuration before starting polling. The Python systemd
# service does not inherit the environment of the separate Plesk Node.js app,
# so BOT_TOKEN and the database URL must be provided by systemd's
# EnvironmentFile or this package's private .env file.
# Keep the values themselves out of logs; only report missing variable names.
CURRENT_STAGE="validate_configuration"
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
write_shell_status "launching" "$CURRENT_STAGE"
exec "$VENV/bin/python" "$BOT_ROOT/main.py"