#!/usr/bin/env bash
# @section QUOTA
# @owner collaborator
# @depends env
set -u
echo
echo "=== [ QUOTA / MODEL ] ==="
_act=$(cat /tmp/hs-stack/active.json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('model',''))" 2>/dev/null)
_ts=$(cat /tmp/hs-stack/active.json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('ts',''))" 2>/dev/null)
printf "  active:    %s\n" "${_act:-unknown}"
printf "  since:     %s\n" "${_ts:-unknown}"

if [ -f /tmp/hs-stack/state.json ]; then
  echo "  --- per-model usage (from state.json) ---"
  python3 -c "
import json
d=json.load(open('/tmp/hs-stack/state.json'))
for m in sorted(d):
    days=d[m]
    for day,v in days.items():
        if isinstance(v,dict):
            print(f\"  {m:42s} {day} items={v.get('items',0):5d} in={v.get('tin',0):7d} out={v.get('tout',0):6d} calls={v.get('calls',0)}\")
        else:
            print(f\"  {m:42s} {day} items={v}\")
"
fi

if [ -f /tmp/hs-stack/limits.json ]; then
  echo "  --- probe cache (limits.json) ---"
  python3 -c "
import json
d=json.load(open('/tmp/hs-stack/limits.json'))
for m in sorted((d.get('models') or {}))[:15]:
    e=d['models'][m]
    print(f\"  {m:42s} http={e.get('http')} rpd={e.get('rpd',0)}\")
"
else
  echo "  limits:    no probe cache"
fi
