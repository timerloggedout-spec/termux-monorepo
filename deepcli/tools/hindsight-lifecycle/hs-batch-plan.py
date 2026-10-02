#!/usr/bin/env python3
"""hs-batch-plan - batch size derived from measurement + model token limits.

No arbitrary cap. The batch size is:
  min( by_window, by_input_tokens, by_output_tokens )

Where:
  by_window       = HTTP_WINDOW_S / measured_per_item_s   (dynamic, from log)
  by_input_tokens = inputTokenLimit / avg_item_tokens
  by_output_tokens = outputTokenLimit / out_tokens_per_item

If no measurements exist, window-based bound is unknown and we use the
smaller of the two token bounds.
"""
import json, os, re, sys
from pathlib import Path

LIM = Path("/tmp/hs-stack/limits.json")
ACT = Path("/tmp/hs-stack/active.json")
LOG = Path("/tmp/mvt-seed.log")

AVG_ITEM_TOKENS = int(os.environ.get("MVT_AVG_ITEM_TOKENS", "2200"))
OUT_PER_ITEM    = int(os.environ.get("MVT_OUT_TOKENS_PER_ITEM", "110"))
HTTP_WINDOW_S   = int(os.environ.get("MVT_HTTP_WINDOW_S", "120"))
MIN_BATCH       = int(os.environ.get("MVT_BATCH_SIZE_MIN", "1"))

def measured_per_item_s():
    """From 'batch #N size=K -> HTTP 200 (Xs)' lines, compute median per-item sec."""
    if not LOG.exists(): return None
    from statistics import median
    per_item = []
    for line in LOG.read_text().splitlines()[-2000:]:
        m = re.search(r'size=(\d+).*?HTTP 200 \(([0-9.]+)s\)', line)
        if m:
            size, wall = int(m.group(1)), float(m.group(2))
            if size > 0 and wall > 0:
                per_item.append(wall / size)
    if len(per_item) < 3: return None
    return median(per_item)

def token_bounds():
    if not (LIM.exists() and ACT.exists()): return None
    lim = json.loads(LIM.read_text())
    act = json.loads(ACT.read_text()).get("model", "")
    m = (lim.get("models") or {}).get(act) or {}
    in_lim = int(m.get("inputTokenLimit") or 0)
    out_lim = int(m.get("outputTokenLimit") or 0)
    if not in_lim or not out_lim: return None
    by_in  = max(1, in_lim  // AVG_ITEM_TOKENS)
    by_out = max(1, out_lim // OUT_PER_ITEM)
    return min(by_in, by_out), in_lim, out_lim, by_in, by_out

def main():
    verbose = "--verbose" in sys.argv
    per_item = measured_per_item_s()
    tb = token_bounds()

    if tb:
        token_cap, in_lim, out_lim, by_in, by_out = tb
    else:
        token_cap, in_lim, out_lim, by_in, by_out = None, 0, 0, 0, 0

    if per_item:
        by_window = max(1, int(HTTP_WINDOW_S / per_item))
    else:
        by_window = None

    candidates = [c for c in (by_window, token_cap) if c]
    size = min(candidates) if candidates else 8
    size = max(size, MIN_BATCH)

    if verbose:
        print(f"per_item_s={per_item:.3f}" if per_item else "per_item_s=(no samples)")
        print(f"window={HTTP_WINDOW_S}s  by_window={by_window}")
        print(f"input_limit={in_lim}  avg_item={AVG_ITEM_TOKENS}  by_in={by_in}")
        print(f"output_limit={out_lim}  out_per_item={OUT_PER_ITEM}  by_out={by_out}")
        print(f"token_cap={token_cap}")
        print(f"chosen={size}")
    else:
        print(size)

if __name__ == "__main__":
    main()
