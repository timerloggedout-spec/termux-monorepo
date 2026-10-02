#!/usr/bin/env bash
# @section GH-QUOTA
# @owner collaborator
# @depends api
set -u
echo
echo "=== [ GITHUB QUOTA ] ==="
_user=$(gh api /user --jq '.login' 2>/dev/null)
if [ -z "$_user" ]; then echo "  gh not authenticated"; exit 0; fi

gh api "/users/${_user}/settings/billing/usage?year=$(date -u +%Y)&month=$(date -u +%-m)" 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    items=[i for i in (d.get('usageItems') or []) if i.get('product')=='Codespaces']
    if items:
        for i in items:
            print(f\"  {i.get('sku','?'):40s}  {i.get('quantity',0):>10.2f} {i.get('unitType','')}\")
    else:
        print('  no codespaces usage items')
except Exception as e:
    print('  err:',e)
"

python3 -c "
from datetime import datetime, timezone
n=datetime.now(timezone.utc)
nx=datetime(n.year+1,1,1,tzinfo=timezone.utc) if n.month==12 else datetime(n.year,n.month+1,1,tzinfo=timezone.utc)
print(f'  reset: {nx.strftime(\"%Y-%m-%d 00:00 UTC\")}  ({(nx-n).days}d)')
"
