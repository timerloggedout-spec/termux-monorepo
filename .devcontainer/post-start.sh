#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/hindsight" || exit 0
[ -d .venv ] || exit 0
. .venv/bin/activate
command -v hindsight-api >/dev/null 2>&1 || exit 0
if pgrep -f hindsight-api >/dev/null 2>&1; then exit 0; fi
export HINDSIGHT_API_PORT=8888
export HINDSIGHT_API_HOST=0.0.0.0
nohup hindsight-api --port 8888 --host 0.0.0.0 > /tmp/hs.log 2>&1 &
for i in $(seq 1 20); do
  sleep 3
  curl -fsS http://localhost:8888/health >/dev/null 2>&1 && break
done
curl -fsS http://localhost:8888/health 2>/dev/null | head -c 200 || true
