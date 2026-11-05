#!/usr/bin/env bash
# Jervis desktop installer — macOS (Apple silicon)
set -euo pipefail

VERSION="v1.0.5"
BASE="https://github.com/TheJarvis-App/jarvis-app/releases/download/$VERSION"
DMG="Jervis-Mac-arm64.dmg"
DEST="$HOME/Downloads/$DMG"
SUMS="$HOME/Downloads/Jervis-SHA256SUMS.txt"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS. On Linux, use the browser assistant in web-assistant/." >&2
  exit 1
fi

mkdir -p "$HOME/Downloads"
echo "Downloading Jervis $VERSION (~196 MB)..."
curl -fL --progress-bar "$BASE/$DMG" -o "$DEST"
echo "Saved to $DEST"

echo "Checking the published SHA256 checksum..."
if curl -fsSL "$BASE/SHA256SUMS.txt" -o "$SUMS"; then
  expected=$(awk -v f="$DMG" 'index($0, f) {print $1; exit}' "$SUMS")
  if [[ -n "$expected" ]]; then
    actual=$(shasum -a 256 "$DEST" | awk '{print $1}')
    if [[ "$expected" != "$actual" ]]; then
      echo "Checksum mismatch — expected $expected, got $actual. NOT opening the disk image." >&2
      exit 1
    fi
    echo "Checksum OK."
  else
    echo "Checksum file did not list $DMG; skipping verification."
  fi
else
  echo "Could not download checksums; skipping verification."
fi

echo "Opening the disk image..."
open "$DEST"
echo "Drag Jervis into Applications, then open it."
echo "If macOS blocks it: System Settings -> Privacy & Security -> Open Anyway."
