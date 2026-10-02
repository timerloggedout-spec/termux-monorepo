#!/usr/bin/env python3
"""hs-codespace-calc — real compute + storage budget from live GitHub API."""
import json, subprocess, sys
from datetime import datetime, timezone

FREE_CORE_HOURS = 120.0
FREE_GB_MONTH = 15.0
HOURS_IN_MONTH = 720.0
CORES = {"standardLinux32gb": 2, "standardLinux32gbX4": 4, "standardLinux32gbX8": 8,
         "basicLinux32gb": 2, "premiumLinux": 8}
DISK = {"standardLinux32gb": 32, "standardLinux32gbX4": 32, "standardLinux32gbX8": 64,
        "basicLinux32gb": 32, "premiumLinux": 64}

def gh_json(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        return None
    try: return json.loads(r.stdout)
    except Exception: return None

def parse_iso(s):
    if not s: return None
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception: return None

rows = gh_json("codespace", "list", "--json",
               "name,state,machineName,createdAt,lastUsedAt,idleTimeoutMinutes,retentionPeriodDays")
if rows is None:
    print("(gh codespace list failed)"); sys.exit(1)

now = datetime.now(timezone.utc)

print("=== CODESPACE USAGE CALC — LIVE ===")
print(f"  now: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
print()
print(f"  {'name':<40s} {'state':<10s} {'cores':>5s} {'wall_h':>7s} {'core_h':>8s} {'disk':>5s} {'gb_mo':>7s}")
total_ch = 0.0; total_gbm = 0.0
for r_ in rows:
    m = r_.get("machineName", "?")
    cores = CORES.get(m, 0)
    disk = DISK.get(m, 0)
    c = parse_iso(r_.get("createdAt"))
    u = parse_iso(r_.get("lastUsedAt"))
    # wall from created -> last used (stopped billing after lastUsed)
    wall = (u - c).total_seconds() / 3600 if (c and u) else 0
    ch = wall * cores
    gb = disk * wall / HOURS_IN_MONTH
    total_ch += ch; total_gbm += gb
    print(f"  {r_['name']:<40s} {r_['state']:<10s} {cores:>5d} {wall:>7.1f} {ch:>8.1f} {disk:>5d} {gb:>7.2f}")

print()
print(f"  TOTAL core_hours:  {total_ch:>8.1f}  / {FREE_CORE_HOURS:.0f}   ({100*total_ch/FREE_CORE_HOURS:>5.1f}%)")
print(f"  TOTAL gb_months:   {total_gbm:>8.2f}  / {FREE_GB_MONTH:.0f}    ({100*total_gbm/FREE_GB_MONTH:>5.1f}%)")
print(f"  compute_gate:      {'BLOCKED' if total_ch >= FREE_CORE_HOURS else 'open'}")
print(f"  storage_gate:      {'BLOCKED' if total_gbm >= FREE_GB_MONTH else 'open'}")
