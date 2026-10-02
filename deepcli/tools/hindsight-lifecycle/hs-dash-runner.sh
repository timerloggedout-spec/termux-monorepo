#!/usr/bin/env bash
# @tool hs-dash-runner
# @version 0.2.0
# @since 2026-10-02
# @change column-aware: reads @col metadata, groups sections
set -u
INST=/home/vscode/.pg0/instances/hindsight/instance.json
export PGHOST=/tmp PGPORT=$(jq -r .port "$INST") PGUSER=$(jq -r .username "$INST")
export PGPASSWORD=$(jq -r .password "$INST") PGDATABASE=$(jq -r .database "$INST")
export PSQL=/home/vscode/.pg0/installation/$(jq -r .version "$INST")/bin/psql
export CS=$(cat /home/vscode/.csname 2>/dev/null || echo "")
_pid=$(pgrep -f "hindsight-api --port 8888" | head -1)
export KEY=$(tr '\0' '\n' < /proc/$_pid/environ 2>/dev/null | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)

echo "============================================================"
echo " HINDSIGHT DASHBOARD  $(date -u +%FT%TZ)"
echo "============================================================"

fail=0; count=0
for s in /tmp/dashboard/sections/*.sh; do
  [ -f "$s" ] || continue
  count=$((count+1)); name="$(basename "$s")"
  if bash "$s" 2>&1; then : ; else fail=$((fail+1)); echo "  FAIL section=$name"; fi
done

echo
echo "=== dashboard receipt ==="
printf "  sections:  %s\n" "$count"
printf "  failures:  %s\n" "$fail"
printf "  finished:  %s\n" "$(date -u +%FT%TZ)"
[ "$fail" -eq 0 ]
