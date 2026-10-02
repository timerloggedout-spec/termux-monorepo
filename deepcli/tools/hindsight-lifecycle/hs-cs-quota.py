#!/usr/bin/env python3
"""hs-cs-quota — codespace quota + usage monitor."""
import json, subprocess, sys, os

cs = os.environ.get("HS_CS_NAME") or open(
    os.path.expanduser("~/.deepcli/cs-hindsight-name.txt")).read().strip()

def gh_json(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None

print("[ CODESPACE QUOTA ]")
rows = gh_json("codespace", "list", "--json",
               "name,state,machineName,lastUsedAt,createdAt,idleTimeoutMinutes")
if rows:
    for r in rows:
        if r["name"] != cs:
            continue
        print(f"  name={r['name']}  state={r['state']}  machine={r['machineName']}")
        print(f"  idle_timeout_min={r.get('idleTimeoutMinutes','?')}")
        print(f"  created={r.get('createdAt','?')}")
        print(f"  last_used={r.get('lastUsedAt','?')}")
else:
    print("  (gh codespace list failed)")

print()
print("[ CODESPACE USAGE — gh api ]")
d = gh_json("api", "/user/codespaces")
if d:
    print(f"  total_codespaces={d.get('total_count', 0)}")
    for x in d.get("codespaces", [])[:5]:
        print(f"    {x['name']}  {x['state']}  {x.get('machine',{}).get('name','?')}")

print()
print("[ BILLING — if org/enterprise scope ]")
me = gh_json("api", "/user")
login = (me or {}).get("login", "")
if login:
    b = gh_json("api", f"/users/{login}/settings/billing/codespaces")
    if b:
        print(f"  minutes_used={b.get('minutes_used','?')}")
        print(f"  minutes_included={b.get('minutes_included','?')}")
        print(f"  paid_storage={b.get('paid_storage',{}).get('total_usage_bytes','?')}")
    else:
        print("  personal account: billing endpoint not available")
