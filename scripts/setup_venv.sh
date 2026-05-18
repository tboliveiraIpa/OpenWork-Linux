#!/usr/bin/env bash
set -euo pipefail
if [ -z "${1-}" ]; then
  VENV_DIR=".venv"
else
  VENV_DIR="$1"
fi

python3 -m venv "$VENV_DIR"
echo "Created venv in $VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt
echo "To activate: source $VENV_DIR/bin/activate"
