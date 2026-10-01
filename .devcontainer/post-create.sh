#!/usr/bin/env bash
set -euo pipefail
echo "[post-create] python=$(python3 --version) libc=$(ldd --version | head -1)"
mkdir -p ~/hindsight && cd ~/hindsight
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip wheel setuptools 2>&1 | tail -1
pip install hindsight-api-slim 2>&1 | tail -4
pip show hindsight-api-slim 2>/dev/null | head -3 || echo "  (install failed)"
echo "[post-create] done"
