#!/usr/bin/env python3
"""hs-cs-quota - codespace quota + usage. Works on Termux and codespace."""
import json, subprocess, sys, os

def resolve_cs():
    v = os.environ.get("HS_CS_NAME")
    if v: return v
    f = os.path.expanduser("~/.deepcli/cs-hindsight-name.txt")
    if os.path.exists(f):
        return open(f).read().strip()
    # On codespace: read codespace name from GITHUB_CODESPACE_TOKEN env or hostname
    h = os.environ.get("CODESPACES_NAME") or os.environ.get("GITHUB_CODESPACE_NAME")
    if h: return h
    # Fallback: pick any Available codespace from gh list
    try:
        r = subprocess.run(["gh", "codespace", "list", "--json", "name,state"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            for c in json.loads(r.stdout):
                if c.get("state") == "Available":
                    return c["name"]
    except Exception:
        pass
    return None

def gh_json(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=15)
    if r.returncode != 0: return None
    try: return json.loads(r.stdout)
    except Exception: return None

cs = resolve_cs()
print("[ CODESPACE QUOTA ]")
if not cs:
    print("  (unable to resolve codespace name)")
else:
    rows = gh_json("codespace", "list", "--json",
                   "name,state,machineName,lastUsedAt,createdAt,idleTimeoutMinutes")
    found = False
    if rows:
        for r in rows:
            if r["name"] != cs: continue
            found = True
            print(f"  name={r['name']}  state={r['state']}  machine={r['machineName']}")
            print(f"  idle={r.get('idleTimeoutMinutes','?')}m  created={r.get('createdAt','?')[:19]}")
            print(f"  last_used={r.get('lastUsedAt','?')[:19]}")
    if not found:
        print(f"  {cs} not in gh list (may be offline from this context)")

    d = gh_json("api", "/user/codespaces")
    if d:
        print(f"  total_codespaces={d.get('total_count', 0)}")
