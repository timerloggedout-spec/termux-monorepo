#!/usr/bin/env bash
# @tool hs-db-runner
# @version 0.1.0
# @since 2026-10-01
# @change codespace-side PG executor, credentials from instance.json
# @doc docs/STANDARDS/FLOWS/DB-ACCESS.md
set -u
INST=/home/vscode/.pg0/instances/hindsight/instance.json
[ -f "$INST" ] || { echo "no instance.json"; exit 1; }
export PGHOST=/tmp PGPORT=$(jq -r .port "$INST")
export PGUSER=$(jq -r .username "$INST") PGPASSWORD=$(jq -r .password "$INST")
export PGDATABASE=$(jq -r .database "$INST")
PSQL=/home/vscode/.pg0/installation/$(jq -r .version "$INST")/bin/psql
if [ "$#" -eq 0 ] || [ "${1:-}" = "-" ]; then
  exec "$PSQL" -tA
fi
exec "$PSQL" -tAf "$1"
