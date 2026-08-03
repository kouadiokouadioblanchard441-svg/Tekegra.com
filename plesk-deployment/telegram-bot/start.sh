#!/usr/bin/env bash
set -Eeuo pipefail

BOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_ROOT"

PYTHON="${BOT_PYTHON:-python3}"
VENV="$BOT_ROOT/.venv"

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet -r "$BOT_ROOT/requirements.txt"

exec "$VENV/bin/python" "$BOT_ROOT/main.py"