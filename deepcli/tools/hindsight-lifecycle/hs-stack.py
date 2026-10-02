#!/usr/bin/env python3
"""Hindsight stack — model pool + RPD tracking + self-aware rotation.

Commands (argv[1]):
  probe       probe every generate+embed model, refresh limits cache
  show        print current limits cache
  rotate      pick next model with RPD headroom, restart Hindsight
  status      pool state, active model, per-model counters, resets
  watch       loop: rotate on 429, re-probe hourly
"""
from __future__ import annotations
import json, os, subprocess, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

HOME = Path.home()
HS = "http://localhost:8888"
BANK = "deepagent::termux-monorepo"
KEY = os.environ.get("HINDSIGHT_API_LLM_API_KEY", "")
GEM = "https://generativelanguage.googleapis.com/v1beta"
STACK = Path("/tmp/hs-stack")
STACK.mkdir(parents=True, exist_ok=True)
STATE = STACK / "state.json"      # per-model counters + resets
LIMITS = STACK / "limits.json"    # cached limits, refreshed on probe
ACTIVE = STACK / "active.json"    # current model + since
LOG = STACK / "stack.log"

# Static fallback (measured 2026-09-02, PT reset). Live probe overrides.
BASELINE = {
    "gemini-3.7-flash":        {"rpd": 20,  "rpm": 5},
    "gemini-3.6-flash":        {"rpd": 20,  "rpm": 5},
    "gemini-3.5-flash":        {"rpd": 20,  "rpm": 5},
    "gemini-3-flash-preview":  {"rpd": 20,  "rpm": 5},
    "gemini-3.5-flash-lite":   {"rpd": 500, "rpm": 15},
    "gemini-3.1-flash-lite":   {"rpd": 500, "rpm": 15},
    "gemini-flash-latest":     {"rpd": 20,  "rpm": 5},
    "gemini-flash-lite-latest":{"rpd": 500, "rpm": 15},
    "gemma-4-26b-a4b-it":      {"rpd": 20,  "rpm": 5},
}
ORDER = [
    "gemini-3.5-flash-lite",   # best free
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemma-4-26b-a4b-it",
]


def log(m):
    line = f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {m}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def load(p, d=None):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return d or {}
    return d or {}


def save(p, d):
    p.write_text(json.dumps(d, indent=2))


def today_pt() -> str:
    # Pacific reset date: UTC-7/8. Use last 8 hours to approximate PT midnight.
    pt = datetime.now(timezone.utc) - timedelta(hours=8)
    return pt.strftime("%Y-%m-%d")


def _post(url, body, key_header="x-goog-api-key", timeout=20):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={key_header: KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()[:800]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:800]
    except Exception as e:
        return 0, str(e).encode()


def list_models():
    req = urllib.request.Request(f"{GEM}/models?pageSize=200",
                                 headers={"x-goog-api-key": KEY})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r).get("models", [])
    except Exception as e:
        log(f"list_models fail: {e}")
        return []


def probe_one(model):
    body = {"contents": [{"parts": [{"text": "ok"}]}],
            "generationConfig": {"maxOutputTokens": 1}}
    s, b = _post(f"{GEM}/models/{model}:generateContent", body)
    metric = ""
    limit = ""
    retry = ""
    try:
        d = json.loads(b)
        for det in (d.get("error", {}).get("details") or []):
            t = det.get("@type", "")
            if t.endswith("QuotaFailure"):
                v = (det.get("violations") or [{}])[0]
                metric = v.get("quotaMetric", "").split("/")[-1]
                limit = str(v.get("quotaValue", ""))
            elif t.endswith("RetryInfo"):
                retry = str(det.get("retryDelay", ""))
    except Exception:
        pass
    return s, {"metric": metric, "limit": limit, "retry": retry}


def cmd_probe():
    models = list_models()
    cache = load(LIMITS, {"probed_at": "", "models": {}})
    candidates = []
    for m in models:
        n = m.get("name", "").replace("models/", "")
        a = m.get("supportedGenerationMethods", []) or []
        if "generateContent" in a and not any(
            k in n for k in ("embed", "image", "tts", "audio", "live", "transcribe")
        ):
            candidates.append(n)
    log(f"probing {len(candidates)} text models")
    for n in candidates:
        s, detail = probe_one(n)
        entry = {
            "http": s,
            "metric": detail["metric"],
            "limit": detail["limit"],
            "retry": detail["retry"],
            "probed_at": time.time(),
        }
        # RPD fallback from baseline
        base = BASELINE.get(n, {})
        entry["rpd"] = int(detail["limit"]) if detail["limit"].isdigit() else base.get("rpd", 0)
        entry["rpm"] = base.get("rpm", 0)
        cache["models"][n] = entry
        log(f"  {n:<30s} http={s}  rpd={entry['rpd']} metric={detail['metric'] or '-'}")
    cache["probed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save(LIMITS, cache)
    log(f"probe done: {len(cache['models'])} models cached")


def cmd_show():
    c = load(LIMITS, {})
    print(f"probed_at: {c.get('probed_at', 'never')}")
    st = load(STATE, {})
    today = today_pt()
    for n, e in sorted(c.get("models", {}).items(), key=lambda x: -x[1].get("rpd", 0)):
        used = st.get(n, {}).get(today, 0)
        rpd = e.get("rpd", 0)
        left = max(0, rpd - used) if rpd else "?"
        print(f"  {n:<32s} rpd={str(rpd):<6s} used={used:<5d} left={left}  http={e.get('http')}")


def pick_next():
    """Return the model with the most headroom. Order-then-headroom."""
    c = load(LIMITS, {})
    st = load(STATE, {})
    today = today_pt()
    # Prefer ORDER list, filter to models the cache knows are usable
    ranked = []
    for n in ORDER:
        e = c.get("models", {}).get(n)
        if not e:
            continue
        # Skip if last probe returned 429 (exhausted)
        if e.get("http") == 429:
            continue
        if e.get("http") not in (200,):
            continue
        rpd = e.get("rpd", 0) or BASELINE.get(n, {}).get("rpd", 0)
        used = st.get(n, {}).get(today, 0)
        headroom = max(0, rpd - used)
        ranked.append((headroom, n, rpd, used))
    ranked.sort(key=lambda x: (-x[0], ORDER.index(x[1]) if x[1] in ORDER else 999))
    if not ranked:
        return None
    headroom, name, rpd, used = ranked[0]
    log(f"pick_next: {name} headroom={headroom} (rpd={rpd}, used={used})")
    return name if headroom > 0 else None


def _live_env_from_api():
    """Pull HINDSIGHT_* env from the running API process, so we preserve keys."""
    import subprocess
    pid = subprocess.run(["pgrep","-f","hindsight-api --port 8888"],
                         capture_output=True, text=True).stdout.strip().split("\n")[0]
    if not pid: return {}
    try:
        raw = open(f"/proc/{pid}/environ","rb").read().decode("utf-8","replace")
    except Exception:
        return {}
    out = {}
    for kv in raw.split("\0"):
        if "=" in kv and kv.startswith("HINDSIGHT_"):
            k, v = kv.split("=", 1)
            out[k] = v
    return out


def restart_hindsight(model: str) -> bool:
    env = os.environ.copy()
    env.update(_live_env_from_api())
    env.update({
        "HINDSIGHT_API_WORKER_ID": "hindsight-termux-monorepo",
        "HINDSIGHT_API_LLM_PROVIDER": "gemini",
        "HINDSIGHT_API_LLM_MODEL": model,  # overrides live env
        "HINDSIGHT_API_LLM_GEMINI_SERVICE_TIER": "flex",
        "HINDSIGHT_API_LLM_PROMPT_CACHE_ENABLED": "false",
        "HINDSIGHT_API_LLM_CACHE_AFFINITY": "none",
        "HINDSIGHT_API_LLM_REASONING_EFFORT": "low",
        "HINDSIGHT_API_EMBEDDINGS_PROVIDER": "google",
        "HINDSIGHT_API_EMBEDDINGS_MODEL": "gemini-embedding-001",
        "HINDSIGHT_API_EMBEDDINGS_GEMINI_OUTPUT_DIMENSIONALITY": "768",
        "HINDSIGHT_API_RERANKER_PROVIDER": "rrf",
        "HINDSIGHT_API_RERANKER_REQUIRED": "false",
        "HINDSIGHT_API_FILE_PARSER": "markitdown",
        "HINDSIGHT_API_PORT": "8888",
        "HINDSIGHT_API_HOST": "0.0.0.0",
    })
    subprocess.run(["pkill", "-9", "-f", "hindsight-api --port 8888"], check=False)
    time.sleep(2)
    subprocess.Popen(
        ["bash", "-lc",
         "cd ~/hindsight && . .venv/bin/activate && "
         "exec hindsight-api --port 8888 --host 0.0.0.0"],
        env=env, stdout=open("/tmp/hs.log", "ab"),
        stderr=subprocess.STDOUT, start_new_session=True,
    )
    for _ in range(40):
        time.sleep(3)
        try:
            with urllib.request.urlopen(f"{HS}/health", timeout=4) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
    return False


def cmd_rotate():
    model = pick_next()
    if not model:
        log("rotate: no model with headroom")
        return 1
    if restart_hindsight(model):
        save(ACTIVE, {
            "model": model,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        log(f"rotate: active {model}")
        return 0
    log(f"rotate: restart failed for {model}")
    return 2


def cmd_status():
    print("=== hs-stack status ===")
    a = load(ACTIVE, {})
    print(f"active:  {a.get('model', '?')}  since {a.get('ts', '?')}")
    st = load(STATE, {})
    today = today_pt()
    c = load(LIMITS, {})
    print(f"reset-date: {today} (Pacific)")
    print(f"probed_at:  {c.get('probed_at', 'never')}")
    print()
    print(f"  {'model':<32s} {'rpd':>5s} {'used':>5s} {'left':>5s}")
    for n in ORDER:
        e = c.get("models", {}).get(n)
        rpd = (e or {}).get("rpd", 0) or BASELINE.get(n, {}).get("rpd", 0)
        used = st.get(n, {}).get(today, 0)
        left = max(0, rpd - used) if rpd else "?"
        print(f"  {n:<32s} {rpd:>5d} {used:>5d} {str(left):>5s}")


def _bump(model):
    st = load(STATE, {})
    today = today_pt()
    st.setdefault(model, {})
    st[model][today] = st[model].get(today, 0) + 1
    save(STATE, st)


def cmd_watch():
    """Loop: probe hourly, rotate on retain 429, bump counter on success."""
    last_probe = 0
    while True:
        now = time.time()
        if now - last_probe > 3600:
            cmd_probe()
            last_probe = now
        a = load(ACTIVE, {})
        model = a.get("model")
        if not model:
            cmd_rotate()
        # probe active model with a retain
        body = {"items": [{"content": "watch tick", "metadata": {"kind": "watch"}}]}
        req = urllib.request.Request(
            f"{HS}/v1/default/banks/{BANK}/memories",
            data=json.dumps(body).encode(), method="POST",
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status == 200:
                    _bump(model)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                log(f"watch: 429 on {model} -> rotate")
                cmd_rotate()
            else:
                log(f"watch: HTTP {e.code} on {model}")
        except Exception as e:
            log(f"watch: err {type(e).__name__}: {e}")
        time.sleep(60)


CMDS = {
    "probe": cmd_probe,
    "show": cmd_show,
    "rotate": cmd_rotate,
    "status": cmd_status,
    "watch": cmd_watch,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd not in CMDS:
        print(__doc__)
        sys.exit(2)
    sys.exit(CMDS[cmd]() or 0)
