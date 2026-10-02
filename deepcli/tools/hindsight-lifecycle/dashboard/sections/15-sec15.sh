#!/usr/bin/env bash
echo "[ BATCH LEDGER - last 8 rows ]"
if [ -f /tmp/mvt-batches.jsonl ]; then
  tail -8 /tmp/mvt-batches.jsonl | python3 -c "
import json, sys
for l in sys.stdin:
    try:
        d = json.loads(l)
        print(f\"  {d['ts'][11:19]}  {d['provider']:10s}  n={d['batch_n']:3d}  size={d['size']:2d}  HTTP {d['http']}  {d['wall_s']:6.1f}s  in={d.get('tokens_in',0)} out={d.get('tokens_out',0)}  {d.get('out_per_sec',0)} tok/s\")
    except Exception:
        pass
"
fi

