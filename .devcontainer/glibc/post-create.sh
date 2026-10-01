#!/usr/bin/env bash
set -euo pipefail
echo "[post-create] python=$(python3 --version) libc=$(ldd --version | head -1)"
mkdir -p ~/hindsight && cd ~/hindsight
export PATH="$HOME/.local/bin:$PATH"
uv venv --python 3.12 2>&1 | tail -2
. .venv/bin/activate
uv pip install hindsight-api-slim 2>&1 | tail -5
pip list 2>/dev/null | grep -i hindsight
echo "[post-create] done"
