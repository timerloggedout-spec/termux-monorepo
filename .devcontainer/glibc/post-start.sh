#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/hindsight" || exit 0
[ -d .venv ] || exit 0
. .venv/bin/activate
if pgrep -f hindsight >/dev/null 2>&1; then exit 0; fi
nohup hindsight-api --port 8888 --host 0.0.0.0 > /tmp/hs.log 2>&1 &
for i in $(seq 1 20); do
  sleep 3
  curl -fsS http://localhost:8888/health >/dev/null 2>&1 && break
done
curl -fsS http://localhost:8888/health | head -c 300
