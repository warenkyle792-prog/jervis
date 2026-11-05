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

# A server left over from an earlier session can still hold the port. Stop only
# that listener so this script always ends up owning the preview.
if command -v ss >/dev/null 2>&1; then
  STALE_PIDS="$(ss -ltnpH 2>/dev/null \
    | grep -E "[:.]${PORT}[[:space:]]" \
    | grep -o 'pid=[0-9]\+' | cut -d= -f2 | sort -u || true)"
  if [ -n "$STALE_PIDS" ]; then
    echo "Stopping stale preview listener(s) on port ${PORT}: ${STALE_PIDS}"
    for pid in $STALE_PIDS; do
      kill "$pid" 2>/dev/null || true
    done
    sleep 0.5
  fi
fi

echo "Jervis preview: http://localhost:${PORT}  (serving site/ on ${HOST}:${PORT})"
exec python3 -m http.server "$PORT" --bind "$HOST" --directory site
