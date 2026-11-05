#!/usr/bin/env bash
# Resume the Jervis preview on port 8000.
# Binds 0.0.0.0 so the Arena preview proxy can reach it.
set -euo pipefail
cd "$(dirname "$0")"

PORT="${JERVIS_PREVIEW_PORT:-8000}"
HOST="${JERVIS_PREVIEW_HOST:-0.0.0.0}"

if [ ! -f site/index.html ]; then
  echo "site/index.html is missing — cannot start the preview." >&2
  exit 1
fi

echo "Jervis preview: http://localhost:${PORT}  (serving site/ on ${HOST}:${PORT})"
exec python3 -m http.server "$PORT" --bind "$HOST" --directory site
