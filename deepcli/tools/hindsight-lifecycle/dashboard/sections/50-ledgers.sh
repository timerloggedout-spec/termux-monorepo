#!/usr/bin/env bash
# @section LEDGERS
# @owner collaborator
# @depends env
set -u
echo
echo "=== [ LEDGERS ] ==="
for name in harvest-ledger multi-ledger exports-ledger; do
 p="$HOME/.deepcli/logs/provenance/${name}.json"
 if [ -f "$p" ]; then
  n="$(python3 - "$p" <<'PY' 2>/dev/null || echo '?'
import json,sys
try: print(len(json.load(open(sys.argv[1]))))
except Exception: print("?")
PY
)"
  printf "  %-18s %s entries\n" "$name" "$n"
 else printf "  %-18s absent\n" "$name"; fi
done
q="$HOME/.deepcli/logs/telemetry/hs-quota.json"
if [ -f "$q" ]; then printf "  quota snapshot:   %s\n" "$(tr '\n' ' ' < "$q" 2>/dev/null | cut -c1-180)"; else echo "  quota snapshot:   absent"; fi
