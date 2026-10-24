#!/usr/bin/env bash
# @section OVERVIEW
# @owner collaborator
# @depends db|api|env
set -u
echo
echo "=== [ OVERVIEW ] ==="
printf "  utc:       %s\n" "$(date -u +%FT%TZ)"
printf "  codespace: %s\n" "${CS:-?}"
_health(){ local p="$1" c; c="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 "http://localhost:${p}/health" 2>/dev/null || true)"; [ -n "$c" ] || c=000; printf "  api:%-4s    %s\n" "$p" "$c"; }
_health 8888; _health 8889
failed=0
_db(){
 local label="$1" query="$2" value
 if [ -n "${PSQL:-}" ] && value="$("$PSQL" -X -v ON_ERROR_STOP=1 -tAc "$query" 2>/dev/null)"; then
  printf "  %-10s %s\n" "$label:" "$value"
 else
  printf "  %-10s unavailable (required database query failed)\n" "$label:" >&2
  failed=1
 fi
}
_db postgres 'SELECT current_database()'
_db banks 'SELECT count(*) FROM banks'
_db memories 'SELECT count(*) FROM memory_units'
python3 - <<'PY' 2>/dev/null || true
import json
from pathlib import Path
try:
 d=json.loads(Path("/tmp/hs-stack/active.json").read_text())
 print(f"  model:     {d.get('model','?')}")
 print(f"  model-since:{d.get('ts','?')}")
except Exception: print("  model:     unknown")
PY
exit "$failed"
