#!/usr/bin/env bash
# @section RUN_STATE
# @owner collaborator
# @depends env
set -u
echo
echo "=== [ RUN STATE ] ==="
if [ -f /tmp/mvt-run-state.json ]; then
python3 - /tmp/mvt-run-state.json <<'PY'
import json,sys
try:
 d=json.load(open(sys.argv[1]))
 for k in ("source","provider","model","bank","ok","fail","429","abort","elapsed_s"):
  if k in d: print(f"  {k:<10} {d[k]}")
except Exception as e: print(f"  state: unreadable ({e})")
PY
else echo "  state:     no active run state"; fi
if [ -f /tmp/mvt-seed.log ]; then
 echo "  batches:   last 8 outcomes"; tail -8 /tmp/mvt-seed.log | sed 's/^/    /'
else echo "  batches:   no mvt-seed.log"; fi
