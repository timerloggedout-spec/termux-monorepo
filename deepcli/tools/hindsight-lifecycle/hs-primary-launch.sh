#!/usr/bin/env bash
# @tool hs-primary-launch
# @version 0.1.0
# @since 2026-10-02
# @change restart :8888 preserving live env, forcing HINDSIGHT_BANK_ID=termux-monorepo::primary
set -u
_main=$(pgrep -f 'hindsight-api --port 8888' | head -1)
[ -z "$_main" ] && { echo "no :8888 pid"; exit 1; }
# capture env before kill
while IFS='=' read -r _k _v; do
  case "$_k" in HINDSIGHT_*) export "$_k=$_v" ;; esac
done < <(tr '\0' '\n' < /proc/$_main/environ)
# override bank
export HINDSIGHT_BANK_ID="termux-monorepo::primary"
export HINDSIGHT_API_PORT=8888
export HINDSIGHT_API_HOST=0.0.0.0

pkill -9 -f 'hindsight-api --port 8888' 2>/dev/null || true
sleep 2
setsid nohup bash -c 'cd ~/hindsight && . .venv/bin/activate && exec hindsight-api --port 8888 --host 0.0.0.0' \
  > /tmp/hs.log 2>&1 < /dev/null &
for i in $(seq 1 30); do sleep 2; c=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://localhost:8888/health 2>/dev/null || echo 000); [ "$c" = "200" ] && break; done
echo "primary_health=$c  pid=$(pgrep -f 'hindsight-api --port 8888' | head -1)"
echo "bank_id=$(tr '\0' '\n' < /proc/$(pgrep -f 'hindsight-api --port 8888' | head -1)/environ | grep HINDSIGHT_BANK_ID | cut -d= -f2-)"
