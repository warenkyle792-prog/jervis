#!/usr/bin/env bash
# Fetch the full upstream Jervis desktop app source (~54 MB).
set -e
cd "$(dirname "$0")"
if [ -d jervis-app-source/.git ]; then
  echo "Updating existing source..."
  git -C jervis-app-source pull --ff-only
else
  git clone --depth 1 https://github.com/TheJarvis-App/jarvis-app.git jervis-app-source
fi
echo ""
echo "Source is in ./jervis-app-source  (gitignored)."
echo "See jervis-app-source/README.md for run-from-source requirements."
