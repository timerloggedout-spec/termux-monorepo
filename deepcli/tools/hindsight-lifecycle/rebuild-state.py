#!/usr/bin/env python3
"""Rebuild /tmp/hs-stack/state.json from llm_requests so rotator DERIVED
matches reality. Counters keyed by model, day = Pacific."""
import json, subprocess
from datetime import datetime, timezone
from pathlib import Path

def psql(q):
    r = subprocess.run(
        ["/home/vscode/.pg0/installation/18.1.0/bin/psql",
         "-h", "/tmp", "-U", "hindsight", "-d", "hindsight", "-tAc", q],
        capture_output=True, text=True, timeout=30,
        env={"PGPASSWORD": "hindsight", "PATH": "/usr/bin:/bin"})
    return (r.stdout or "").strip()

rows = psql("""
SELECT model,
       to_char(started_at - interval '8 hours', 'YYYY-MM-DD') AS day_pt,
       count(*),
       coalesce(sum(input_tokens),0),
       coalesce(sum(output_tokens),0)
FROM llm_requests
WHERE started_at > now() - interval '7 days'
GROUP BY 1,2 ORDER BY 1,2;
""").splitlines()

state = {}
for line in rows:
    p = line.split("|")
    if len(p) != 5: continue
    model, day, calls, tin, tout = p
    if not model: model = "(unset)"
    state.setdefault(model, {})
    state[model][day] = {"items": int(calls), "tin": int(tin), "tout": int(tout), "calls": int(calls), "wall": 0.0}

p = Path("/tmp/hs-stack/state.json")
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(state, indent=2))
print(f"wrote {p}  models={len(state)}")

# also fix active.json ts
ap = Path("/tmp/hs-stack/active.json")
ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
ap.write_text(json.dumps({"model": "gemini-3.1-flash-lite", "ts": ts}, indent=2))
print(f"wrote {ap}  ts={ts}")
