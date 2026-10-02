#!/usr/bin/env bash
set -u
INST=/home/vscode/.pg0/instances/hindsight/instance.json
export PGHOST=/tmp PGPORT=$(jq -r .port "$INST") PGUSER=$(jq -r .username "$INST")
export PGPASSWORD=$(jq -r .password "$INST") PGDATABASE=$(jq -r .database "$INST")
export PSQL=/home/vscode/.pg0/installation/$(jq -r .version "$INST")/bin/psql
export CS=$(cat /home/vscode/.csname 2>/dev/null || echo "")
_pid=$(pgrep -f "hindsight-api --port 8888" | head -1)
export KEY=$(tr '\0' '\n' < /proc/$_pid/environ 2>/dev/null | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)
for s in /tmp/dashboard/sections/*.sh; do
  [ -f "$s" ] || continue
  bash "$s" 2>&1
done
