#!/usr/bin/env python3
"""hs-batch-plan - measured + theoretical batch size.

Priority:
  1. Measured: parse wall times, pick size maximizing items/sec under window.
  2. Theoretical: inputTokenLimit / avg_item_tokens, outputTokenLimit / out_per_item.
  3. Fallback: 8.
"""
import json, os, re, sys
from pathlib import Path
from statistics import median

LIM = Path("/tmp/hs-stack/limits.json")
ACT = Path("/tmp/hs-stack/active.json")
LOG = Path("/tmp/mvt-seed.log")

AVG_ITEM_TOKENS = int(os.environ.get("MVT_AVG_ITEM_TOKENS", "2200"))
OUT_PER_ITEM = int(os.environ.get("MVT_OUT_TOKENS_PER_ITEM", "110"))
MAX_BATCH = int(os.environ.get("MVT_BATCH_SIZE_MAX", "16"))
MIN_BATCH = int(os.environ.get("MVT_BATCH_SIZE_MIN", "4"))
HTTP_WINDOW_S = int(os.environ.get("MVT_HTTP_WINDOW_S", "120"))

def parse_log():
    if not LOG.exists(): return []
    pairs = []
    for line in LOG.read_text().splitlines()[-500:]:
        m = re.search(r'size=(\d+).*?HTTP 200 \(([0-9.]+)s\)', line)
        if m:
            pairs.append((int(m.group(1)), float(m.group(2))))
    return pairs

def measured():
    samples = parse_log()
    if len(samples) < 3: return None
    buckets = {}
    for size, wall in samples:
        buckets.setdefault(size, []).append(wall)
    best = None
    for size, walls in buckets.items():
        med = median(walls)
        if med <= 0 or med > HTTP_WINDOW_S: continue
        ips = size / med
        if best is None or ips > best[1]:
            best = (size, ips, med, len(walls))
    return best

def theoretical():
    if not (LIM.exists() and ACT.exists()): return None
    lim = json.loads(LIM.read_text())
    act = json.loads(ACT.read_text()).get("model", "")
    m = (lim.get("models") or {}).get(act) or {}
    in_lim = int(m.get("inputTokenLimit") or 0)
    out_lim = int(m.get("outputTokenLimit") or 0)
    if not in_lim or not out_lim: return None
    by_input = max(1, in_lim // AVG_ITEM_TOKENS)
    by_output = max(1, out_lim // OUT_PER_ITEM)
    raw = min(by_input, by_output)
    return min(MAX_BATCH, max(MIN_BATCH, raw))

verbose = "--verbose" in sys.argv
meas = measured()
theo = theoretical()
if meas:
    size, ips, med_s, n = meas
    reason = f"measured: {size}/{med_s:.1f}s = {ips:.3f} ips over {n}"
elif theo:
    size = theo
    reason = f"theoretical cap: {size}"
else:
    size = 8
    reason = "fallback 8"

size = min(MAX_BATCH, max(MIN_BATCH, size))

if verbose:
    print(f"chosen={size}  max={MAX_BATCH}  window={HTTP_WINDOW_S}s")
    print(f"reason={reason}")
    print(f"samples={len(parse_log())}")
else:
    print(size)
