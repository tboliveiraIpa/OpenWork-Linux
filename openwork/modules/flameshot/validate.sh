#!/usr/bin/env bash
set -euo pipefail
if command -v flameshot >/dev/null 2>&1; then
  echo "flameshot OK"
  exit 0
else
  echo "flameshot NOT FOUND" >&2
  exit 1
fi
