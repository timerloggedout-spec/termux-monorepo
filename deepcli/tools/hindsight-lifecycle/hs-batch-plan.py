#!/usr/bin/env python3
"""hs-batch-plan — batch size from live token limits + measured per-item time.

size = min( inputTokenLimit/avg_item,
            outputTokenLimit/out_per_item,
            HTTP_WINDOW_S / per_item_s )

per_item_s: measured median if >=3 samples, else PRIOR (env-overridable).
Never caps. Never returns None if a bound exists.
"""
import json, os, re, sys, urllib.request, subprocess
from pathlib import Path
from statistics import median

ACT_CANDIDATES = [Path("/tmp/hs-stack/active.json"),
                  Path(os.path.expanduser("~/.deepcli/.llm-active.json"))]
LOG = Path("/tmp/mvt-seed.log")

AVG_ITEM_TOKENS = int(os.environ.get("MVT_AVG_ITEM_TOKENS", "2200"))
OUT_PER_ITEM    = int(os.environ.get("MVT_OUT_PER_ITEM", "110"))
HTTP_WINDOW_S   = int(os.environ.get("MVT_HTTP_WINDOW_S", "120"))
MIN_BATCH       = int(os.environ.get("MVT_BATCH_SIZE_MIN", "1"))
PRIOR_PER_ITEM  = float(os.environ.get("MVT_PRIOR_PER_ITEM_S", "9.4"))
FALLBACK_LIMITS = {"gemini": (1048576, 65536), "qwen": (262144, 65536),
                   "gemma": (262144, 65536), "llama": (131072, 32768),
                   "mistral": (131072, 32768), "deepseek": (131072, 8192)}

def read_active():
    for p in ACT_CANDIDATES:
        if p.exists():
            try:
                return json.loads(p.read_text()).get("model", "")
            except Exception:
                pass
    return ""

def api_key():
    try:
        p = subprocess.run(["pgrep", "-f", "hindsight-api --port 8888"],
                           capture_output=True, text=True).stdout.strip().split("\n")[0]
        if not p: return None
        for line in open(f"/proc/{p}/environ").read().split("\0"):
            if line.startswith("HINDSIGHT_API_LLM_API_KEY="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return None

def live_limits(model):
    if not model: return None
    key = api_key()
    if not key: return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}?key={key}"
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.load(r)
        return int(d.get("inputTokenLimit", 0)), int(d.get("outputTokenLimit", 0))
    except Exception:
        return None

def family_limits(model):
    m = (model or "").lower()
    for k, v in FALLBACK_LIMITS.items():
        if k in m: return v
    return None

def measured_per_item():
    if not LOG.exists(): return None
    xs = []
    for line in LOG.read_text().splitlines()[-2000:]:
        mm = re.search(r'size=(\d+).*?HTTP 200 \(([0-9.]+)s\)', line)
        if mm:
            s, w = int(mm.group(1)), float(mm.group(2))
            if s > 0 and w > 0: xs.append(w / s)
    return median(xs) if len(xs) >= 3 else None

def main():
    verbose = "--verbose" in sys.argv
    model = read_active()
    limits = live_limits(model) or family_limits(model) or (0, 0)
    in_lim, out_lim = limits

    p = measured_per_item()
    per_item = p if p else PRIOR_PER_ITEM

    by_in  = (in_lim  // AVG_ITEM_TOKENS) if in_lim  else None
    by_out = (out_lim // OUT_PER_ITEM)    if out_lim else None
    by_win = int(HTTP_WINDOW_S / per_item) if per_item else None

    candidates = [c for c in (by_in, by_out, by_win) if c]
    size = max(MIN_BATCH, min(candidates)) if candidates else 8

    if verbose:
        print(f"model={model or '(unset)'}")
        print(f"  limits: in={in_lim} out={out_lim}")
        print(f"  avg_item={AVG_ITEM_TOKENS}  out_per_item={OUT_PER_ITEM}")
        print(f"  by_input={by_in}  by_output={by_out}")
        print(f"  per_item_s={per_item:.2f} (measured={p is not None})  window={HTTP_WINDOW_S}s  by_window={by_win}")
        print(f"  chosen={size}")
    else:
        print(size)

if __name__ == "__main__":
    main()
