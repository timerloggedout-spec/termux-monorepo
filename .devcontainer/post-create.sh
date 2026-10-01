#!/usr/bin/env bash
set -euo pipefail
echo "[pc] os=$(grep ^PRETTY_NAME /etc/os-release | cut -d= -f2-)"
echo "[pc] python=$(python3 --version 2>&1) libc=$(ldd --version 2>&1 | head -1)"
grep -q "Debian\|Ubuntu" /etc/os-release || { echo "[pc] FATAL: not Debian/Ubuntu"; exit 1; }
mkdir -p ~/hindsight && cd ~/hindsight
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip wheel setuptools 2>&1 | tail -1
pip install hindsight-api-slim 2>&1 | tail -3
pip show hindsight-api-slim 2>/dev/null | head -2
ls -la .venv/bin/hindsight-api 2>/dev/null || echo "[pc] no hindsight-api binary"
echo "[pc] done"
