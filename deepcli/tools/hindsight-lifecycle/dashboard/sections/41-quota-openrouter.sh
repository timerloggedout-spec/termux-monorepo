#!/usr/bin/env bash
# @section QUOTA-OPENROUTER
# @owner collaborator
# @depends api
set -u
echo
echo "=== [ OPENROUTER QUOTA ] ==="
_pid=$(pgrep -f "hindsight-api --port 8888" | head -1)
_or=$(tr '\0' '\n' < /proc/$_pid/environ 2>/dev/null | grep '^OPENROUTER_API_KEY=' | cut -d= -f2-)
if [ -z "$_or" ]; then echo "  (no OPENROUTER_API_KEY)"; exit 0; fi
echo "  key_prefix: ${_or:0:12}..."

echo "  --- /auth/key (live) ---"
curl -sS --max-time 8 -H "Authorization: Bearer $_or" https://openrouter.ai/api/v1/auth/key 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin).get('data') or {}
    rl=d.get('rate_limit') or {}
    print(f\"  limit={d.get('limit','unlimited')}  usage={d.get('usage','0')}  remaining={d.get('limit_remaining','inf')}\")
    print(f\"  rpm={rl.get('requests','?')}  interval={rl.get('interval','?')}  tier={d.get('tier','?')}\")
except Exception as e: print('  err:',e)
"

echo "  --- /credits (live) ---"
curl -sS --max-time 8 -H "Authorization: Bearer $_or" https://openrouter.ai/api/v1/credits 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin).get('data') or {}
    print(f\"  credits_total={d.get('total_credits','?')}  used={d.get('total_usage','?')}\")
except Exception: pass
"

echo "  --- state.json OR models ---"
python3 -c "
import json
from pathlib import Path
p=Path('/tmp/hs-stack/state.json')
if not p.exists(): raise SystemExit
d=json.loads(p.read_text())
for m in sorted(d):
    if not m.startswith(('qwen','meta-llama','openrouter')): continue
    for day,v in d[m].items():
        if isinstance(v,dict):
            print(f\"  {m:38s} {day} calls={v.get('calls',0):5d} in={v.get('tin',0):8d} out={v.get('tout',0):6d}\")
" 2>/dev/null
