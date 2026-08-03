#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT/../dist"
ARCHIVE="$OUT_DIR/lucky-jet-ai-bot-plesk.zip"

mkdir -p "$OUT_DIR"
rm -f "$ARCHIVE"

cd "$ROOT/.."
zip -qr "$ARCHIVE" "$(basename "$ROOT")" \
  -x "$(basename "$ROOT")/node_modules/*" \
     "$(basename "$ROOT")/.env" \
     "$(basename "$ROOT")/telegram-bot/.env" \
     "$(basename "$ROOT")/**/__pycache__/*" \
     "$(basename "$ROOT")/**/*.pyc" \
     "$(basename "$ROOT")/server/*.ts" \
     "$(basename "$ROOT")/server/*/*.ts" \
     "$(basename "$ROOT")/server/*/*/*.ts" \
     "$(basename "$ROOT")/src/*" \
     "$(basename "$ROOT")/src/**/*" \
     "$(basename "$ROOT")/vite.config.ts" \
     "$(basename "$ROOT")/tsconfig.json"

printf 'Created %s (%s bytes)\n' "$ARCHIVE" "$(stat -c '%s' "$ARCHIVE")"