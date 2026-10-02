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

python3 - <<'PYEOF'
import json
from pathlib import Path
st = json.loads(Path("/tmp/hs-stack/state.json").read_text()) if Path("/tmp/hs-stack/state.json").exists() else {}
lim = json.loads(Path("/tmp/hs-stack/limits.json").read_text()) if Path("/tmp/hs-stack/limits.json").exists() else {}

print()
print("  [ GEMINI - usage + probe cache ]")
print(f"  {'model':42s} {'calls':>7s} {'in':>9s} {'out':>7s} {'http':>5s} {'rpd':>5s}")
gem_models = sorted([m for m in st if not m.startswith(("qwen","meta-llama","openrouter","("))])
for m in gem_models:
    calls = sum(v.get("calls",0) if isinstance(v,dict) else v for v in st[m].values())
    tin   = sum(v.get("tin",0)   if isinstance(v,dict) else 0 for v in st[m].values())
    tout  = sum(v.get("tout",0)  if isinstance(v,dict) else 0 for v in st[m].values())
    e = (lim.get("models") or {}).get(m, {})
    print(f"  {m:42s} {calls:7d} {tin:9d} {tout:7d} {str(e.get('http','-')):>5s} {str(e.get('rpd',0)):>5s}")

print()
print("  [ OPENROUTER - usage ]")
print(f"  {'model':42s} {'calls':>7s} {'in':>9s} {'out':>7s}")
or_models = sorted([m for m in st if m.startswith(("qwen","meta-llama","openrouter"))])
if not or_models:
    print("  (no OpenRouter activity)")
for m in or_models:
    calls = sum(v.get("calls",0) if isinstance(v,dict) else v for v in st[m].values())
    tin   = sum(v.get("tin",0)   if isinstance(v,dict) else 0 for v in st[m].values())
    tout  = sum(v.get("tout",0)  if isinstance(v,dict) else 0 for v in st[m].values())
    print(f"  {m:42s} {calls:7d} {tin:9d} {tout:7d}")
PYEOF

echo
echo "  [ LIVE OPENROUTER ]"
_or=$(tr '\0' '\n' < /proc/$(pgrep -f 'hindsight-api --port 8888' | head -1)/environ 2>/dev/null | grep '^OPENROUTER_API_KEY=' | cut -d= -f2-)
if [ -n "${_or:-}" ]; then
  curl -sS --max-time 8 -H "Authorization: Bearer $_or" https://openrouter.ai/api/v1/auth/key 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin).get('data') or {}
    rl=d.get('rate_limit') or {}
    print(f\"    limit={d.get('limit','unlimited')} usage={d.get('usage','0')} remaining={d.get('limit_remaining','inf')}\")
    print(f\"    rpm={rl.get('requests','?')} interval={rl.get('interval','?')} tier={d.get('tier','?')}\")
except Exception as e: print('    err:',e)
"
  curl -sS --max-time 8 -H "Authorization: Bearer $_or" https://openrouter.ai/api/v1/credits 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin).get('data') or {}
    print(f\"    credits_total={d.get('total_credits','?')} used={d.get('total_usage','?')}\")
except Exception: pass
"
fi

echo "  --- full probe cache ---"
python3 -c "
import json
d=json.load(open('/tmp/hs-stack/limits.json'))
for m in sorted((d.get('models') or {})):
    e=d['models'][m]
    print(f\"  {m:42s} http={e.get('http')} rpd={e.get('rpd',0)}\")
" 2>/dev/null || echo "  (no limits cache)"
