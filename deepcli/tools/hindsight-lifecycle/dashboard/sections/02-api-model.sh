#!/usr/bin/env bash
echo "[ API MODEL ]"
for p in 8888 8889; do
  pid=$(pgrep -f "hindsight-api --port $p" | head -1)
  if [ -z "$pid" ]; then echo "  :$p DEAD"; continue; fi
  m=$(tr '\0' '\n' < /proc/$pid/environ | grep '^HINDSIGHT_API_LLM_MODEL=' | cut -d= -f2-)
  prov=$(tr '\0' '\n' < /proc/$pid/environ | grep '^HINDSIGHT_API_LLM_PROVIDER=' | cut -d= -f2-)
  echo "  :$p provider=$prov model=$m"
done

INST=/home/vscode/.pg0/instances/hindsight/instance.json
PSQL=""
if [ -f "$INST" ]; then
  export PGHOST=/tmp PGPORT=$(jq -r .port "$INST")
  export PGUSER=$(jq -r .username "$INST") PGPASSWORD=$(jq -r .password "$INST")
  export PGDATABASE=$(jq -r .database "$INST")
  PSQL=/home/vscode/.pg0/installation/$(jq -r .version "$INST")/bin/psql
fi

echo
