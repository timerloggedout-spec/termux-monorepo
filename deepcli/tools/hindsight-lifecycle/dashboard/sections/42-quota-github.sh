#!/usr/bin/env bash
# @section QUOTA-GITHUB
# @owner collaborator
# @depends ledger
set -u
echo
echo "=== [ GITHUB QUOTA — all metrics vs free tier ] ==="
LED="$HOME/.deepcli/logs/quota-ledger.json"
if [ ! -f "$LED" ]; then echo "  (no ledger — run write-quota-ledger.py)"; exit 0; fi

python3 -c "
import json, sys
from pathlib import Path
from datetime import datetime, timezone
d = json.loads(Path('$LED').read_text())
g = d.get('github', {}) or {}
f = d.get('free_tier', {}) or {}
G = d.get('gates', {}) or {}
rst = d.get('next_reset_utc','?')[:10]
days = d.get('days_until_reset','?')
print(f\"  reset: {rst}  ({days}d)\")
print()
print('  [ CODESPACES ]')
cu = g.get('codespaces_compute_core_hours',0)
cl = f.get('codespaces_compute_core_hours',120)
pct = 100*cu/cl if cl else 0
bar = '█' * int(pct/5) + '·' * (20 - int(pct/5))
print(f\"    compute  {cu:>7.1f} / {cl:>5.0f} core-h   [{bar}] {pct:>5.1f}%\")
su = G.get('codespaces_storage',{}).get('used',0)
sl = f.get('codespaces_storage_gb_month',15)
print(f\"    storage  {su:>7.3f} / {sl:>5.1f} GB-mo\")
print()
print('  [ ACTIONS ]')
for k, lab in [('actions_linux_minutes','linux'),('actions_slim_minutes','linux-slim'),
               ('actions_windows_minutes','windows'),('actions_macos_minutes','macos'),
               ('actions_storage_gb_hours','storage')]:
    v = g.get(k,0)
    if 'storage' in k:
        print(f\"    {lab:<14s} {v:>9.2f} GB-h\")
    else:
        lim_key = 'actions_'+('linux' if 'slim' not in k else 'linux')+'_minutes'
        lim = f.get(lim_key, 2000)
        pct = 100*v/lim if lim else 0
        print(f\"    {lab:<14s} {v:>9.0f} / {lim:>5.0f} min  ({pct:.1f}%)\")
print()
print('  [ COST AS IF PAID ]')
print(f\"    gross    \${g.get('gross_usd',0):>9.4f}\")
print(f\"    net      \${g.get('net_usd',0):>9.4f}\")
"
