#!/usr/bin/env bash
# @section QUOTA-GEMINI
# @owner collaborator
# @depends api
set -u
echo
echo "=== [ GEMINI QUOTA ] ==="
_act=""
[ -f /tmp/hs-stack/active.json ] && _act=$(python3 -c "import json;print(json.load(open('/tmp/hs-stack/active.json')).get('model',''))" 2>/dev/null)
echo "  active:  $_act"

# live probe against active model
_pid=$(pgrep -f "hindsight-api --port 8888" | head -1)
_k=$(tr '\0' '\n' < /proc/$_pid/environ 2>/dev/null | grep '^HINDSIGHT_API_LLM_API_KEY=' | cut -d= -f2-)
if [ -n "$_k" ] && [ -n "$_act" ]; then
  _r=$(curl -sS --max-time 10 -o /tmp/probe.json -w '%{http_code}' \
    "https://generativelanguage.googleapis.com/v1beta/models/${_act}:generateContent?key=${_k}" \
    -H 'Content-Type: application/json' \
    -d '{"contents":[{"parts":[{"text":"q"}]}],"generationConfig":{"maxOutputTokens":1}}' 2>/dev/null)
  echo "  live_probe: HTTP $_r"
  if [ "$_r" = "429" ]; then
    python3 -c "
import json
d=json.load(open('/tmp/probe.json'))
for det in (d.get('error',{}).get('details') or []):
    t=det.get('@type','')
    if t.endswith('QuotaFailure'):
        v=(det.get('violations') or [{}])[0]
        print('  live_limit:', v.get('quotaValue','?'), 'metric:', v.get('quotaMetric','').split('/')[-1])
    if t.endswith('RetryInfo'):
        print('  retry_in:  ', det.get('retryDelay','?'))
" 2>/dev/null
  fi
fi

echo "  --- state.json per-model ---"
python3 -c "
import json
from pathlib import Path
p=Path('/tmp/hs-stack/state.json')
if not p.exists(): print('  (no state)'); raise SystemExit
d=json.loads(p.read_text())
for m in sorted(d):
    if m.startswith(('qwen','meta-llama','openrouter','(')): continue
    for day,v in d[m].items():
        if isinstance(v,dict):
            print(f\"  {m:36s} {day} calls={v.get('calls',0):5d} in={v.get('tin',0):8d} out={v.get('tout',0):6d}\")
" 2>/dev/null

echo "  --- limits.json probe cache (text-gen models only) ---"
python3 -c "
import json
from pathlib import Path
p=Path('/tmp/hs-stack/limits.json')
if not p.exists(): print('  (no cache)'); raise SystemExit
d=json.loads(p.read_text())
ms=d.get('models') or {}
n200=sum(1 for m in ms.values() if m.get('http')==200)
print(f'  probed: {len(ms)}  available(200): {n200}')
for m in sorted(ms):
    e=ms[m]
    if 'embed' in m or 'tts' in m or 'image' in m or 'audio' in m: continue
    print(f\"  {m:40s} http={e.get('http'):>4} rpd={e.get('rpd',0):>4}\")
" 2>/dev/null
