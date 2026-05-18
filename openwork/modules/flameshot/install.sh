#!/usr/bin/env bash
set -euo pipefail
echo "Installing Flameshot via native package manager"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y flameshot
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y flameshot
else
  echo "No supported package manager found. Please install flameshot manually."
  exit 2
fi
