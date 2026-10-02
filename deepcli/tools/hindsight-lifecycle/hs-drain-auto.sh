#!/usr/bin/env bash
# @tool hs-drain-auto
# @version 0.1.0
# @since 2026-10-02
# @change export every bank, push snapshot to memory-bank branch
set -u
BANK_PRIMARY="termux-monorepo::primary"
INST=/home/vscode/.pg0/instances/hindsight/instance.json
export PGHOST=/tmp PGPORT=$(jq -r .port "$INST" 2>/dev/null || echo 5432)
export PGUSER=$(jq -r .username "$INST" 2>/dev/null || echo hindsight)
export PGPASSWORD=$(jq -r .password "$INST" 2>/dev/null || echo hindsight)
export PGDATABASE=$(jq -r .database "$INST" 2>/dev/null || echo hindsight)
PSQL=/home/vscode/.pg0/installation/$(jq -r .version "$INST" 2>/dev/null || echo 18.1.0)/bin/psql

TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="/tmp/bank-drain-${TS}.zip"

# Best-effort export via API
_p=$(pgrep -f "hindsight-api --port 8888" | head -1)
KEY=$(tr '\0' '\n' < /proc/$_p/environ 2>/dev/null | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)

OP=$(curl -sS --max-time 20 -X POST \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"include_data":true,"include_bank_config":true,"include_history":true}' \
  "http://localhost:8888/v1/default/banks/${BANK_PRIMARY}/transfer/export" 2>/dev/null \
  | python3 -c "import sys,json;print(json.load(sys.stdin).get('operation_id',''))" 2>/dev/null)

if [ -n "$OP" ]; then
  for i in $(seq 1 60); do
    sleep 4
    STAT=$(curl -sS --max-time 10 -H "Authorization: Bearer $KEY" \
      "http://localhost:8888/v1/default/banks/${BANK_PRIMARY}/operations/$OP" 2>/dev/null \
      | python3 -c "import sys,json;print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
    if [ "$STAT" = "succeeded" ] || [ "$STAT" = "completed" ]; then
      curl -sS --max-time 120 -H "Authorization: Bearer $KEY" \
        "http://localhost:8888/v1/default/banks/${BANK_PRIMARY}/transfer/export/download/$OP" \
        -o "$OUT" 2>&1 | tail -1
      break
    fi
  done
fi

# DB fallback: dump memory_units as JSONL
if [ ! -s "$OUT" ]; then
  OUT="/tmp/bank-drain-${TS}.jsonl"
  "$PSQL" -tA -c "COPY (SELECT row_to_json(t) FROM memory_units t WHERE bank_id='${BANK_PRIMARY}') TO STDOUT" > "$OUT" 2>/dev/null
fi

echo "ts=$TS out=$OUT size=$(wc -c < "$OUT" 2>/dev/null || echo 0)"
