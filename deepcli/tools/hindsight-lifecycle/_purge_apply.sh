#!/usr/bin/env bash
set -u
INST=/home/vscode/.pg0/instances/hindsight/instance.json
export PGHOST=/tmp PGPORT=$(jq -r .port "$INST") PGUSER=$(jq -r .username "$INST")
export PGPASSWORD=$(jq -r .password "$INST") PGDATABASE=$(jq -r .database "$INST")
PSQL=/home/vscode/.pg0/installation/$(jq -r .version "$INST")/bin/psql
"$PSQL" -v purge_apply=1 -f /tmp/purge-stale.sql 2>&1 | tail -8
