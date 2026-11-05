#!/usr/bin/env bash
# Refresh the vendored Jervis desktop source in jervis-app-source/ from upstream.
# Warning: overwrites everything in that folder except VENDORED.md.
set -euo pipefail
cd "$(dirname "$0")"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Fetching upstream..."
git clone --depth 1 -q https://github.com/TheJarvis-App/jarvis-app.git "$TMP/upstream"
COMMIT=$(git -C "$TMP/upstream" rev-parse --short HEAD)
rm -rf "$TMP/upstream/.git"

mkdir -p jervis-app-source
find jervis-app-source -mindepth 1 -maxdepth 1 ! -name VENDORED.md -exec rm -rf {} +
cp -a "$TMP/upstream/." jervis-app-source/

echo "Refreshed jervis-app-source/ from upstream commit $COMMIT."
echo "Review with: git status   (VENDORED.md still names the previous commit — update it if needed.)"
