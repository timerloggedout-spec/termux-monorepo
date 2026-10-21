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
if [ -n "${PSQL:-}" ]; then
  printf "  postgres:  %s\n" "$("$PSQL" -tAc 'SELECT current_database()' 2>/dev/null || echo down)"
  printf "  banks:     %s\n" "$("$PSQL" -tAc 'SELECT count(*) FROM banks' 2>/dev/null || echo '?')"
  printf "  memories:  %s\n" "$("$PSQL" -tAc 'SELECT count(*) FROM memory_units' 2>/dev/null || echo '?')"
fi
python3 - <<'PY' 2>/dev/null || true
import json
from pathlib import Path
try:
 d=json.loads(Path("/tmp/hs-stack/active.json").read_text())
 print(f"  model:     {d.get('model','?')}")
 print(f"  model-since:{d.get('ts','?')}")
except Exception: print("  model:     unknown")
PY
