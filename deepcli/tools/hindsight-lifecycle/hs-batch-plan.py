#!/usr/bin/env python3
"""hs-batch-plan - batch size from live model token limits + measured per-item time.

size = min( inputTokenLimit/avg_item_tokens,
            outputTokenLimit/out_tokens_per_item,
            HTTP_WINDOW_S / measured_per_item_s )

No hardcoded cap. Token limits fetched live from Gemini models API.
"""
import json, os, re, sys, urllib.request
from pathlib import Path
from statistics import median

ACT = Path("/tmp/hs-stack/active.json")
LOG = Path("/tmp/mvt-seed.log")

AVG_ITEM_TOKENS = int(os.environ.get("MVT_AVG_ITEM_TOKENS", "2200"))
OUT_PER_ITEM    = int(os.environ.get("MVT_OUT_TOKENS_PER_ITEM", "110"))
HTTP_WINDOW_S   = int(os.environ.get("MVT_HTTP_WINDOW_S", "120"))
MIN_BATCH       = int(os.environ.get("MVT_BATCH_SIZE_MIN", "1"))
PRIOR_PER_ITEM_S = float(os.environ.get("MVT_PRIOR_PER_ITEM_S", "9.4"))

FALLBACK = {"gemini": (1048576, 65536), "qwen": (262144, 65536),
            "gemma": (262144, 65536), "llama": (131072, 32768)}

def api_key():
    import subprocess
    p = subprocess.run(["pgrep", "-f", "hindsight-api --port 8888"],
                       capture_output=True, text=True).stdout.strip().split("\n")[0]
    if not p: return None
    for line in open(f"/proc/{p}/environ").read().split("\0"):
        if line.startswith("HINDSIGHT_API_LLM_API_KEY="):
            return line.split("=", 1)[1]
    return None

def live_token_limits(model):
    key = api_key()
    if not key: return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}?key={key}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.load(r)
        return int(d.get("inputTokenLimit", 0)), int(d.get("outputTokenLimit", 0))
    except Exception:
        return None

def family_defaults(model):
    m = (model or "").lower()
    for k, v in FALLBACK.items():
        if k in m: return v
    return None

def per_item_s():
    if not LOG.exists(): return None
    per = []
    for line in LOG.read_text().splitlines()[-2000:]:
        mm = re.search(r'size=(\d+).*?HTTP 200 \(([0-9.]+)s\)', line)
        if mm:
            s, w = int(mm.group(1)), float(mm.group(2))
            if s > 0 and w > 0: per.append(w / s)
    return median(per) if len(per) >= 3 else None

def main():
    verbose = "--verbose" in sys.argv
    model = json.loads(ACT.read_text()).get("model", "") if ACT.exists() else ""
    limits = live_token_limits(model) or family_defaults(model) or (0, 0)
    in_lim, out_lim = limits

    by_in  = in_lim  // AVG_ITEM_TOKENS if in_lim  else None
    by_out = out_lim // OUT_PER_ITEM    if out_lim else None
    p = per_item_s()
    by_win = int(HTTP_WINDOW_S / (p or PRIOR_PER_ITEM_S))

    candidates = [c for c in (by_in, by_out, by_win) if c]
    size = max(MIN_BATCH, min(candidates))

    if verbose:
        print(f"model={model}")
        print(f"  live inputTokenLimit={in_lim}  outputTokenLimit={out_lim}")
        print(f"  avg_item_tokens={AVG_ITEM_TOKENS}  out_per_item={OUT_PER_ITEM}")
        print(f"  by_input={by_in}  by_output={by_out}")
        print(f"  per_item_s={p if p else PRIOR_PER_ITEM_S}  window={HTTP_WINDOW_S}s  by_window={by_win}")
        print(f"  chosen={size}")
    else:
        print(size)

if __name__ == "__main__":
    main()
