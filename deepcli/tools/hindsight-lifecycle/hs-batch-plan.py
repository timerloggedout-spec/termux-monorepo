#!/usr/bin/env python3
"""hs-batch-plan - measured batch size, not theoretical token limits.

Reads:
  /tmp/hs-stack/limits.json   model input/output token limits
  /tmp/hs-stack/active.json   active model
  /tmp/mvt-seed.log           per-batch HTTP wall times

Logic:
  - Hindsight serializes items WITHIN one POST. Batch size does NOT reduce
    LLM call count (1 call per item regardless). It only reduces HTTP overhead.
  - Workers run concurrently. Real throughput = workers * items_per_sec.
  - If batch wall time is superlinear (16 items takes >2x 8 items), reduce.
  - If linear, keep batch at a size that fits a reasonable HTTP window.
"""
import json, os, re, sys
from pathlib import Path

LIM = Path("/tmp/hs-stack/limits.json")
ACT = Path("/tmp/hs-stack/active.json")
LOG = Path("/tmp/mvt-seed.log")

DEFAULT_BATCH = int(os.environ.get("MVT_BATCH_SIZE_DEFAULT", "8"))
MAX_BATCH = int(os.environ.get("MVT_BATCH_SIZE_MAX", "16"))
HTTP_WINDOW_S = int(os.environ.get("MVT_HTTP_WINDOW_S", "120"))

def parse_log():
    """Return [(items, wall_s), ...] from 'batch #N size=K -> HTTP 200 (Xs)'"""
    if not LOG.exists(): return []
    pairs = []
    for line in LOG.read_text().splitlines()[-500:]:
        m = re.search(r'size=(\d+).*?HTTP 200 \(([0-9.]+)s\)', line)
        if m:
            pairs.append((int(m.group(1)), float(m.group(2))))
    return pairs

def measured_batch(candidates=(4, 8, 16, 24)):
    """Given wall-time samples, pick batch size maximizing items/sec under window."""
    samples = parse_log()
    if len(samples) < 3:
        return None
    from statistics import median
    buckets = {}
    for items, wall in samples:
        buckets.setdefault(items, []).append(wall)
    best = None
    for size, walls in buckets.items():
        med = median(walls)
        if med <= 0: continue
        if med > HTTP_WINDOW_S: continue
        items_per_sec = size / med
        if best is None or items_per_sec > best[1]:
            best = (size, items_per_sec, med, len(walls))
    return best

def main():
    verbose = "--verbose" in sys.argv
    lim = json.loads(LIM.read_text()) if LIM.exists() else {}
    act = json.loads(ACT.read_text()).get("model", "") if ACT.exists() else ""
    m = (lim.get("models") or {}).get(act) or {}
    in_lim = int(m.get("inputTokenLimit") or 1_048_576)
    out_lim = int(m.get("outputTokenLimit") or 65_536)

    measured = measured_batch()
    if measured:
        size, ips, med_s, n = measured
        reason = f"measured: {size} items/{med_s:.1f}s = {ips:.3f} items/s over {n} samples"
    else:
        # Theoretical cap from tokens, default fallback
        size = DEFAULT_BATCH
        reason = f"no samples yet; default {DEFAULT_BATCH}"
    size = min(size, MAX_BATCH)

    if verbose:
        print(f"model={act}")
        print(f"  input_limit={in_lim}  output_limit={out_lim}")
        print(f"  chosen={size}  max={MAX_BATCH}  window={HTTP_WINDOW_S}s")
        print(f"  reason={reason}")
        # Show all samples
        samples = parse_log()
        if samples:
            print(f"  samples={len(samples)}: " + ", ".join(f"{i}i:{w:.1f}s" for i, w in samples[-8:]))
    else:
        print(size)

if __name__ == "__main__":
    main()
