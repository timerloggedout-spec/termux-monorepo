#!/usr/bin/env bash
# @tool hs-sovereign-launch
# @version 0.1.0
# @since 2026-10-01
# @change canonical sovereign-loop launcher (never inline bash -c)
# @doc docs/STANDARDS/FLOWS/HINDSIGHT-LIFECYCLE-LIB.md
set -u

_main=$(pgrep -f 'hindsight-api --port 8888' | head -1)
if [ -n "$_main" ]; then
  export HINDSIGHT_API_KEY=$(tr '\0' '\n' < /proc/$_main/environ | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)
fi
echo "api_key_len=${#HINDSIGHT_API_KEY}"

pkill -9 -f 'sovereign-run.sh' 2>/dev/null || true
pkill -9 -f 'mvt-seed.py'      2>/dev/null || true
sleep 2

rm -f /tmp/sovereign.log /tmp/mvt-seed.log /tmp/sovereign-src.idx
echo 0 > /tmp/sovereign-src.idx

setsid nohup bash -c 'while true; do bash /tmp/sovereign-run.sh >> /tmp/sovereign.log 2>&1; sleep 300; done' \
  > /dev/null 2>&1 < /dev/null &

sleep 15

echo "--- pids ---"
pgrep -af 'sovereign-run|mvt-seed' | head -4
echo
echo "--- sovereign.log ---"
head -15 /tmp/sovereign.log 2>/dev/null
echo
echo "--- mvt-seed.log ---"
head -20 /tmp/mvt-seed.log 2>/dev/null
