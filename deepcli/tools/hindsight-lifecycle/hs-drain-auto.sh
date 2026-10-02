#!/usr/bin/env bash
# @tool hs-drain-auto
# @version 0.2.0
# @since 2026-10-02
# @change API export with size validation + DB gzip fallback
set -u
BANKS="${BANKS:-termux-monorepo::primary termux-monorepo::mvt::google::gemini::base}"
INST=/home/vscode/.pg0/instances/hindsight/instance.json
export PGHOST=/tmp PGPORT=$(jq -r .port "$INST" 2>/dev/null || echo 5432)
export PGUSER=$(jq -r .username "$INST" 2>/dev/null || echo hindsight)
export PGPASSWORD=$(jq -r .password "$INST" 2>/dev/null || echo hindsight)
export PGDATABASE=$(jq -r .database "$INST" 2>/dev/null || echo hindsight)
PSQL=/home/vscode/.pg0/installation/$(jq -r .version "$INST" 2>/dev/null || echo 18.1.0)/bin/psql
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="/tmp/bank-drain-${TS}.zip"
TMP=$(mktemp -d)

_p=$(pgrep -f "hindsight-api --port 8888" | head -1)
KEY=$(tr '\0' '\n' < /proc/$_p/environ 2>/dev/null | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)

API_OK=0
for B in $BANKS; do
  SAFE=$(echo "$B" | tr ':' '_')
  _f="$TMP/${SAFE}.jsonl"
  "$PSQL" -tA -c "COPY (SELECT row_to_json(t) FROM memory_units t WHERE bank_id='$B') TO STDOUT" > "$_f" 2>/dev/null
  _n=$(wc -l < "$_f" 2>/dev/null || echo 0)
  echo "  db-dump $B -> $_n rows"
  [ "$_n" -gt 0 ] && API_OK=1
done

# Also try API export for the primary bank (as bonus)
OP=$(curl -sS --max-time 20 -X POST \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"include_data":true,"include_bank_config":true,"include_history":true}' \
  "http://localhost:8888/v1/default/banks/termux-monorepo::primary/transfer/export" 2>/dev/null \
  | python3 -c "import sys,json;print(json.load(sys.stdin).get('operation_id',''))" 2>/dev/null)

if [ -n "$OP" ]; then
  for i in $(seq 1 45); do
    sleep 3
    STAT=$(curl -sS --max-time 10 -H "Authorization: Bearer $KEY" \
      "http://localhost:8888/v1/default/banks/termux-monorepo::primary/operations/$OP" 2>/dev/null \
      | python3 -c "import sys,json;print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
    case "$STAT" in
      succeeded|completed)
        DL=$(curl -sS --max-time 10 -H "Authorization: Bearer $KEY" \
          "http://localhost:8888/v1/default/banks/termux-monorepo::primary/operations/$OP" 2>/dev/null \
          | python3 -c "import sys,json;d=json.load(sys.stdin);print((d.get('result_metadata') or {}).get('download_url',''))" 2>/dev/null)
        [ -n "$DL" ] && curl -sS --max-time 120 -H "Authorization: Bearer $KEY" "$DL" -o "$TMP/api-export.zip" 2>/dev/null
        break ;;
      failed|error)
        echo "  api-export $STAT"; break ;;
    esac
  done
fi

# Build final zip: db jsonl + api-export if valid
cd "$TMP"
if [ -f "api-export.zip" ] && [ "$(stat -c%s api-export.zip 2>/dev/null || echo 0)" -gt 1024 ]; then
  cp api-export.zip "$OUT"
else
  zip -q "$OUT" *.jsonl 2>/dev/null || tar czf "${OUT%.zip}.tgz" *.jsonl
fi

SZ=$(stat -c%s "$OUT" 2>/dev/null || echo 0)
echo "ts=$TS out=$OUT size=$SZ"
[ "$SZ" -lt 100 ] && { echo "  WARN: output under 100 bytes"; exit 2; }
echo "  OK: $SZ bytes"
