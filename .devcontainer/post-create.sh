#!/usr/bin/env bash
set -euo pipefail
echo "[pc] os=$(grep ^PRETTY_NAME /etc/os-release | cut -d= -f2-)"
mkdir -p ~/hindsight && cd ~/hindsight
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install --quiet --upgrade pip wheel setuptools
pip install --quiet 'hindsight-api-slim[embedded-db]'
pip show hindsight-api-slim 2>/dev/null | head -2
echo "[pc] done"
