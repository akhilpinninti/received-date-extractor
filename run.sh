#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv-linux"

if [ "$#" -ne 2 ]; then
    echo "Usage: ./run.sh input_folder output.csv"
    exit 2
fi

INPUT_DIR="$1"
OUTPUT_CSV="$2"

if [ ! -d "$INPUT_DIR" ]; then
    echo "ERROR: Input directory does not exist: $INPUT_DIR"
    exit 2
fi

if ! command -v python3.12 >/dev/null 2>&1; then
    echo "ERROR: Python 3.12 is required."
    exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
    python3.12 -m venv "$VENV_DIR"
fi

PYTHON="$VENV_DIR/bin/python"

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON" "$ROOT_DIR/main.py" "$INPUT_DIR" "$OUTPUT_CSV"