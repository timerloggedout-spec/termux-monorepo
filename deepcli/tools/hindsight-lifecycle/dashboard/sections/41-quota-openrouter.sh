#!/usr/bin/env bash
# @section QUOTA-OPENROUTER
# @owner collaborator
# @depends ledger
set -u
echo
echo "=== [ OPENROUTER QUOTA — live vs free tier ] ==="
LED="$HOME/.deepcli/logs/quota-ledger.json"
if [ ! -f "$LED" ]; then echo "  (no ledger)"; exit 0; fi
python3 -c "
import json
from pathlib import Path
d = json.loads(Path('$LED').read_text())
o = d.get('openrouter', {}) or {}
f = d.get('free_tier', {}) or {}
print(f\"  limit:     {o.get('limit','unlimited')}\")
print(f\"  usage:     {o.get('usage',0)}\")
print(f\"  remaining: {o.get('remaining','inf')}\")
print(f\"  rpm:       {o.get('rpm','?')}\")
print(f\"  credits:   total={o.get('credits_total','?')} used={o.get('credits_used','?')}\")
print(f\"  free_rpd:  {f.get('openrouter_rpd_free', 50)} (before \\$10 lifetime top-up)\")
"
