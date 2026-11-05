#!/usr/bin/env bash
# Verify the Jervis preview on port 8000 is serving this repo's page.
set -euo pipefail
PORT="${JERVIS_PREVIEW_PORT:-8000}"
BASE="http://127.0.0.1:${PORT}"

echo "Health endpoint:"
curl -fsS -m 5 "${BASE}/health.json"
echo
curl -fsS -m 5 -o /dev/null -w "GET /           -> HTTP %{http_code}\n" "${BASE}/"
curl -fsS -m 5 -o /dev/null -w "GET /health.json -> HTTP %{http_code}\n" "${BASE}/health.json"
