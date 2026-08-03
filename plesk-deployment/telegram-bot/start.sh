#!/usr/bin/env bash
set -Eeuo pipefail

BOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_ROOT"

PYTHON="${BOT_PYTHON:-python3}"
VENV="$BOT_ROOT/.venv"

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

# Some hosting environments set PIP_USER globally. That is incompatible with
# a virtualenv ("user site-packages are not visible in this virtualenv"), so
# explicitly keep both pip operations inside the bot virtualenv.
"$VENV/bin/python" -m pip install --no-user --quiet --upgrade pip
"$VENV/bin/python" -m pip install --no-user --quiet -r "$BOT_ROOT/requirements.txt"

# Validate the configuration before starting polling.  Plesk often runs this
# script through Supervisor with a different environment from the Node app.
# Keep the values themselves out of logs; only report missing variable names.
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
        ". Configure these variables in the Python/Supervisor process "
        "or create telegram-bot/.env."
    )
PY

exec "$VENV/bin/python" "$BOT_ROOT/main.py"