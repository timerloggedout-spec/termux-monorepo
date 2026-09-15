#!/usr/bin/env bash
# setup.sh — bootstrap ArchWiz dependencies across environments.
# Supports: Replit (no venv), Termux (no venv), local Linux/macOS (venv).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- Detect environment ----------
_detect_env() {
    if [ -d /data/data/com.termux ]; then
        echo "termux"
    elif [ -n "${REPL_ID:-}" ] || [ -n "${REPLIT_DOMAINS:-}" ] || [ -n "${REPLIT_DB_URL:-}" ]; then
        echo "replit"
    else
        echo "local"
    fi
}
ARCHWIZ_ENV="${ARCHWIZ_ENV:-$(_detect_env)}"
echo "Environment detected: $ARCHWIZ_ENV"

# ---------- Install Python deps ----------
case "$ARCHWIZ_ENV" in
  termux)
    # Termux: pkg provides ruff; install Python libs system-wide
    echo "Installing Python libs (Termux)..."
    pip install --quiet --upgrade pip
    pip install --quiet -r "$SCRIPT_DIR/requirements-base.txt"
    ;;
  replit)
    # Replit: no venv support; install directly to the Nix/system Python.
    # pip install --user is also acceptable here.
    echo "Installing Python libs (Replit)..."
    pip install --quiet --upgrade pip
    pip install --quiet -r "$SCRIPT_DIR/requirements-base.txt"
    ;;
  *)
    # Local: use a venv to avoid polluting the system Python
    echo "Installing Python libs (local venv)..."
    VENV="$SCRIPT_DIR/.venv"
    if [ ! -d "$VENV" ]; then
        python3 -m venv "$VENV"
    fi
    # shellcheck source=/dev/null
    source "$VENV/bin/activate"
    pip install --quiet --upgrade pip
    pip install --quiet -r "$SCRIPT_DIR/requirements-base.txt"
    echo "  Activate with: source .venv/bin/activate"
    ;;
esac

# ---------- Validate archwiz.config imports ----------
echo "Validating archwiz.config..."
PYTHONPATH="$SCRIPT_DIR" python3 - <<'PY'
from archwiz import config as aw_config
from archwiz.config import ARCHWIZ_DIR, SESSION_STORE, MULTI_AI_TOKENS_DIR
print(f"  env:           {aw_config.ARCHWIZ_ENV}")
print(f"  archwiz_root:  {aw_config.ARCHWIZ_ROOT}")
print(f"  ARCHWIZ_DIR:   {ARCHWIZ_DIR}")
print(f"  SESSION_STORE: {SESSION_STORE}")
print(f"  TOKENS_DIR:    {MULTI_AI_TOKENS_DIR}")
PY

echo "Done."
echo "For heavy dependencies (flair, torch, watchexec, hyperfine), install them separately in an x86_64 environment."
