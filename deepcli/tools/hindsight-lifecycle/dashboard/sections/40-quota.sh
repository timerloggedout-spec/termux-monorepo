#!/usr/bin/env bash
# @section QUOTA
# @owner collaborator
# @depends env
set -u
echo
echo "=== [ QUOTA / MODEL ] ==="
python3 - <<'PY' 2>/dev/null || true
import json
from pathlib import Path
try:
 a=json.loads(Path("/tmp/hs-stack/active.json").read_text())
 print(f"  active:    {a.get('model','?')}")
 print(f"  since:     {a.get('ts','?')}")
except Exception: print("  active:    unknown")
try:
 d=json.loads(Path("/tmp/hs-stack/limits.json").read_text())
 st=json.loads(Path("/tmp/hs-stack/state.json").read_text()) if Path("/tmp/hs-stack/state.json").exists() else {}
 from datetime import datetime,timezone,timedelta
 today=(datetime.now(timezone.utc)-timedelta(hours=8)).strftime("%Y-%m-%d")
 order=["gemini-3.5-flash-lite","gemini-3.1-flash-lite","gemini-flash-lite-latest","gemini-3.7-flash","gemini-3.6-flash","gemini-3.5-flash","gemini-3-flash-preview","gemini-flash-latest","gemma-4-26b-a4b-it"]
 for n in order:
  e=d.get("models",{}).get(n)
  if e:
   r=int(e.get("rpd") or 0); u=int(st.get(n,{}).get(today,0)); print(f"  {n:<30} rpd={r:<4} used={u:<4} left={max(0,r-u) if r else '?'}")
except Exception: print("  limits:    no probe cache")
PY
