#!/usr/bin/env bash
# @section QUOTA-GEMINI
# @owner collaborator
# @depends ledger
set -u
echo
echo "=== [ GEMINI QUOTA — per model ] ==="
LED="$HOME/.deepcli/logs/quota-ledger.json"
if [ ! -f "$LED" ]; then echo "  (no ledger)"; exit 0; fi
python3 -c "
import json
from pathlib import Path
d = json.loads(Path('$LED').read_text())
g = d.get('gemini', {}) or {}
st = g.get('state') or {}
print(f\"  probe_cache: {g.get('probe_cache_models',0)} models, {g.get('available_200',0)} available (HTTP 200)\")
print()
print(f\"  {'model':<42s} {'calls':>7s} {'in':>9s} {'out':>8s}\")
for m in sorted(st):
    if m.startswith(('qwen','meta-llama','openrouter','(')): continue
    for day, v in st[m].items():
        if isinstance(v, dict):
            print(f\"  {m:<42s} {v.get('calls',0):>7d} {v.get('tin',0):>9d} {v.get('tout',0):>8d}\")
print()
print('  Free tier RPD per model:')
print('    flash-lite family: 500/day each')
print('    flash family:       20/day each')
"
