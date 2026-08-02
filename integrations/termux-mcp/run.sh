#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
  python -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install "mcp[cli]>=1.2.0,<2"

if [[ -n "${TERMUX_MCP_DIR:-}" ]]; then
  pip install -e "$TERMUX_MCP_DIR"
fi

exec python "$SCRIPT_DIR/serve.py"
