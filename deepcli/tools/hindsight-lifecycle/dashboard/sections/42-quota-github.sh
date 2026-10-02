#!/usr/bin/env bash
# @section QUOTA-GITHUB
# @owner collaborator
# @depends api
set -u
echo
echo "=== [ GITHUB CODESPACE QUOTA ] ==="
_user=$(gh api /user --jq '.login' 2>/dev/null)
[ -z "$_user" ] && { echo "  (gh not authenticated)"; exit 0; }
echo "  user: $_user"

# live billing usage — Enhanced billing platform
_year=$(date -u +%Y); _mon=$(date -u +%-m)
_usage=$(gh api "/users/${_user}/settings/billing/usage?year=${_year}&month=${_mon}" 2>/dev/null || echo "{}")
echo "  --- billing/usage (this month) ---"
echo "$_usage" | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    items=[i for i in (d.get('usageItems') or []) if i.get('product')=='Codespaces']
    if not items:
        print('  (no Codespaces usage items — account not migrated to Enhanced Billing)')
    for i in items:
        q=i.get('quantity',0)
        print(f\"  {i.get('sku','?'):28s} {q:>10.2f} {i.get('unitType','')}\")
except Exception as e: print('  err:',e)
"

# live per-codespace calc — compute + storage
echo "  --- per-codespace (compute + storage budget) ---"
gh codespace list --json name,state,machineName,createdAt,lastUsedAt 2>/dev/null | python3 -c "
import json,sys
from datetime import datetime, timezone
now=datetime.now(timezone.utc)
CORES={'standardLinux32gb':2,'standardLinux32gbX4':4,'standardLinux32gbX8':8}
DISK={'standardLinux32gb':32,'standardLinux32gbX4':32,'standardLinux32gbX8':64}
def parse(s):
    if not s: return None
    try: return datetime.fromisoformat(s.replace('Z','+00:00'))
    except: return None
rows=json.load(sys.stdin)
total_ch=0.0; total_gbm=0.0
print(f\"  {'name':<38s} {'state':<10s} {'cores':>5s} {'wall_h':>7s} {'core_h':>7s} {'disk_gb':>7s} {'gb_mo':>7s}\")
for r in rows:
    m=r.get('machineName','standardLinux32gb')
    cores=CORES.get(m,2); disk=DISK.get(m,32)
    c=parse(r.get('createdAt')); u=parse(r.get('lastUsedAt'))
    wall=(now-c).total_seconds()/3600 if c else 0
    ch=wall*cores; gb=disk*wall/720
    total_ch+=ch; total_gbm+=gb
    print(f\"  {r['name']:<38s} {r['state']:<10s} {cores:>5d} {wall:>7.1f} {ch:>7.1f} {disk:>7d} {gb:>7.2f}\")
print()
print(f\"  TOTAL core_hours:  {total_ch:>7.1f}  / 120  ({100*total_ch/120:>5.1f}%)\")
print(f\"  TOTAL gb_months:   {total_gbm:>7.2f}  /  15  ({100*total_gbm/15:>5.1f}%)\")
print(f\"  compute_gate:      {'BLOCKED' if total_ch>=120 else 'open'}\")
print(f\"  storage_gate:      {'BLOCKED' if total_gbm>=15 else 'open'}\")
"

# reset date
echo "  --- reset ---"
python3 -c "
from datetime import datetime, timezone
n=datetime.now(timezone.utc)
nx=datetime(n.year+1,1,1,tzinfo=timezone.utc) if n.month==12 else datetime(n.year,n.month+1,1,tzinfo=timezone.utc)
print('  next reset:', nx.strftime('%Y-%m-%d'), '00:00 UTC')
print('  days:      ', (nx-n).days)
"

# current codespace resume state
_cs=$(cat "$HOME/.deepcli/cs-hindsight-name.txt" 2>/dev/null)
if [ -n "$_cs" ]; then
  echo "  --- primary $_cs ---"
  gh codespace view -c "$_cs" --json name,state,machineName,idleTimeoutMinutes,retentionPeriodDays,lastUsedAt 2>/dev/null | python3 -c "
import json,sys
try:
    r=json.load(sys.stdin)
    for k in ('state','machineName','idleTimeoutMinutes','retentionPeriodDays','lastUsedAt'):
        print(f'  {k:22s} {r.get(k,"?")}')
except Exception: pass
"
fi
