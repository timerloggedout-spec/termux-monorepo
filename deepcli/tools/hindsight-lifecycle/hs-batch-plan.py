#!/usr/bin/env python3
"""hs-batch-plan — compute optimal BATCH_SIZE from model token limits."""
import json, os, sys
from pathlib import Path

LIM = Path("/tmp/hs-stack/limits.json")
ACT = Path("/tmp/hs-stack/active.json")
AVG_ITEM_TOKENS = int(os.environ.get("MVT_AVG_ITEM_TOKENS", "2200"))
OUT_TOKENS_PER_ITEM = int(os.environ.get("MVT_OUT_TOKENS_PER_ITEM", "110"))
WORKER_CONCURRENCY = int(os.environ.get("MVT_CONCURRENCY", "4"))

if not LIM.exists() or not ACT.exists():
    print("8"); sys.exit(0)

limits = json.loads(LIM.read_text())
active = json.loads(ACT.read_text()).get("model", "")

# Find model in limits cache
m = (limits.get("models") or {}).get(active) or {}
# Fall back to known family defaults if limits cache lacks the field
in_limit = int(m.get("inputTokenLimit") or m.get("in") or 1_048_576)
out_limit = int(m.get("outputTokenLimit") or m.get("out") or 65_536)

# Per-item token cost
# In: whole batch input is per-item so item count = in_limit / avg_item
by_input = max(1, in_limit // AVG_ITEM_TOKENS)
# Out: whole batch output must fit in one response for Hindsight chunker
# Hindsight chunks by tokens, so this is generous
by_output = max(1, out_limit // OUT_TOKENS_PER_ITEM)

# Practical bound: 8 is Hindsight's shared_slots default
raw = min(by_input, by_output)
# Cap at 16 to leave room for concurrent POSTs
planned = min(16, raw)

if len(sys.argv) > 1 and sys.argv[1] == "--verbose":
    print(f"model={active}")
    print(f"  inputTokenLimit={in_limit}  outputTokenLimit={out_limit}")
    print(f"  avg_item_tokens={AVG_ITEM_TOKENS}  out_per_item={OUT_TOKENS_PER_ITEM}")
    print(f"  by_input={by_input}  by_output={by_output}")
    print(f"  planned_batch={planned}  concurrency={WORKER_CONCURRENCY}")
else:
    print(planned)
