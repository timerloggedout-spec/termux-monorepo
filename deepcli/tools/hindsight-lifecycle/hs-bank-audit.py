#!/usr/bin/env python3
"""hs-bank-audit — classify every bank by convention state."""
import subprocess, sys

SQL = """
SELECT bank_id,
       count(*) AS facts,
       round(extract(epoch from (now() - max(created_at)))/60)::int AS mins_since
FROM memory_units
GROUP BY bank_id ORDER BY max(created_at) DESC NULLS LAST;
"""

def psql(q):
    r = subprocess.run(
        ["/home/vscode/.pg0/installation/18.1.0/bin/psql",
         "-h", "/tmp", "-U", "hindsight", "-d", "hindsight", "-tAc", q],
        capture_output=True, text=True, timeout=60,
        env={"PGPASSWORD": "hindsight", "PATH": "/usr/bin:/bin"})
    return (r.stdout or "").strip()

def classify(bank_id, mins):
    if bank_id.endswith("::primary"): return "OK-primary"
    parts = bank_id.split("::")
    if len(parts) >= 2 and parts[1] == "mvt":
        if len(parts) >= 7: return "OK-mvt"
        return "PARTIAL-mvt"
    if bank_id.startswith("deepagent::"):
        return "STALE-v1" if mins > 30 else "ACTIVE-v1"
    return "UNKNOWN"

rows = psql(SQL).splitlines()
print(f"{'bank_id':<78s} {'facts':>6s} {'mins':>6s}  convention")
for line in rows:
    p = line.split("|")
    if len(p) != 3: continue
    bank, facts, mins = p
    try: m = int(mins)
    except: m = 9999
    print(f"  {bank:<76s} {facts:>6s} {mins:>6s}  {classify(bank, m)}")
