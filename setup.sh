#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================="
echo "   Classical Maze - Quick Setup and Launcher (Unix/macOS)"
echo "========================================================="
echo ""

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "[ERROR] Python 3 was not found in PATH."
    echo "Please install Python 3.8+ using your package manager (e.g. apt, brew)."
    exit 1
fi

PY_BIN="python3"
if ! command -v python3 &>/dev/null; then
    PY_BIN="python"
fi

$PY_BIN setup.py

read -p "Would you like to run the simulation now? [Y/n]: " RUN_NOW
RUN_NOW=${RUN_NOW:-Y}
if [[ "$RUN_NOW" =~ ^[Yy]$ ]]; then
    echo ""
    echo "[*] Starting simulation..."
    if [ -f ".venv/bin/python" ]; then
        .venv/bin/python main.py
    else
        $PY_BIN main.py
    fi
fi
