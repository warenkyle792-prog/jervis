#!/usr/bin/env bash
# Start Jervis on macOS / Linux.
set -e
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
echo "Starting Jervis at http://127.0.0.1:8765  (Ctrl+C to stop)"
exec "$PYTHON" -m jarvis.web
