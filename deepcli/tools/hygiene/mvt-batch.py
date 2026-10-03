import os, re, sys, json, time, pathlib, subprocess, collections

HOME = pathlib.Path.home()
sys.path.insert(0, str(HOME / "deepcli"))
sys.path.insert(0, str(HOME / ".local" / "lib"))

from deepcli._v1_cache import read_session, last_msg_ts
from deepcli._v1_events import scan_session as scan_events
from deepcli._v1_preflight import score as pre_score, env_state

SS       = HOME / ".deepcli" / "session_store"
OUT_TOT  = HOME / ".deepcli" / "watchdog" / "mvt-totals.json"
OUT_TRI  = HOME / ".deepcli" / "logs" / "hygiene" / "mvt-trials.jsonl"
OUT_WIN  = HOME / ".deepcli" / "watchdog" / "mvt-winners.json"
CACHE    = HOME / ".deepcli" / "watchdog" / "mvt-batch-cache.json"
EXC      = HOME / ".local" / "lib" / "mvt_exclude.py"

def log(m=""): print(m, flush=True)

# ── load exclude helper ──
try:
    import mvt_exclude
except ImportError:
    class _N:
        def is_excluded(self, *a, **k): return False
    mvt_exclude = _N()

# ── load mvt-score as module ──
MVT_MOD_PATH = HOME / "deepcli" / "tools" / "hygiene" / "mvt-score"
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
loader = SourceFileLoader("mvt_score_mod", str(MVT_MOD_PATH))
spec = spec_from_loader("mvt_score_mod", loader)
mvt = module_from_spec(spec); sys.modules["mvt_score_mod"] = mvt
loader.exec_module(mvt)
log(f"  loaded mvt-score ({len([k for k in dir(mvt) if not k.startswith('_')])} symbols)")

# ── enumerate sessions (deduped across primary/secondary/flat) ──
def all_sessions():
    seen = {}
    for base in (SS/"primary", SS/"secondary", SS):
        if not base.is_dir(): continue
        for f in base.glob("*.json"):
            if f.stem in seen: continue
            seen[f.stem] = f
    return seen

sessions = all_sessions()
log(f"  {len(sessions)} unique sessions")

# ── load cache ──
try:
    cache = json.loads(CACHE.read_text())
except Exception:
    cache = {}

# ── score all ──
t0 = time.time()
all_trials = []
skipped_excl = 0
skipped_short = 0
scored = 0
errors = 0
session_meta = {}

for i, (sid, f) in enumerate(sessions.items(), 1):
    try: mt = f.stat().st_mtime
    except Exception: mt = 0
    ck = f"v2:{sid}:{mt}"

    # cache hit
    if ck in cache:
        rec = cache[ck]
        if rec.get("skip"):
            if rec["skip"] == "excluded": skipped_excl += 1
            else: skipped_short += 1
            continue
        for tr in rec.get("trials", []):
            tr["session"] = sid
            all_trials.append(tr)
        session_meta[sid] = rec.get("meta", {})
        scored += 1
        continue

    # load
    msgs = read_session(f)
    if not msgs or len(msgs) < 4:
        cache[ck] = {"skip": "short"}; skipped_short += 1
        continue

    # exclude check
    try:
        first = mvt.content_of(msgs[0])[:200] if isinstance(msgs[0], dict) else ""
        if mvt_exclude.is_excluded(sid, first):
            cache[ck] = {"skip": "excluded"}; skipped_excl += 1
            continue
    except Exception:
        pass

    # score
    try:
        trials = mvt.score_session(f)
    except Exception as e:
        cache[ck] = {"skip": f"err:{type(e).__name__}"}; errors += 1
        continue

    # attach preflight level to each trial
    try:
        ev_recs = scan_events(f)
        flat_events = []
        for r in ev_recs:
            flat_events.extend(r["symbols"])
        pf = pre_score(flat_events)
    except Exception:
        pf = {"level": "?", "reason": ""}

    for tr in trials:
        tr["session"] = sid
        tr["preflight_level"] = pf.get("level", "?")
        tr["preflight_reason"] = pf.get("reason", "")

    cache[ck] = {"trials": trials, "meta": {
        "n_msgs": len(msgs), "pf_level": pf.get("level", "?"),
    }}
    session_meta[sid] = cache[ck]["meta"]
    for tr in trials: all_trials.append(tr)
    scored += 1

    if i % 100 == 0:
        log(f"  ... {i}/{len(sessions)}  trials={len(all_trials)}  cached={scored}")

elapsed = time.time() - t0
log(f"  done in {elapsed:.1f}s  trials={len(all_trials)}  sessions_scored={scored}  excl={skipped_excl}  short={skipped_short}  err={errors}")

# save cache
CACHE.write_text(json.dumps(cache))

# ── aggregate ──
totals = {"L0": 0, "L1": 0, "L2": 0}
by_lang = collections.defaultdict(lambda: {"L0": 0, "L1": 0, "L2": 0})
by_hash = collections.defaultdict(lambda: {"L0": 0, "L1": 0, "L2": 0, "lang": None,
                                            "bytes": 0, "head": "", "sessions": set()})
by_preflight = collections.Counter()
by_signal = collections.Counter()

for tr in all_trials:
    lv = tr.get("level")
    if lv not in (0, 1, 2): continue
    key = f"L{lv}"
    totals[key] += 1
    lang = tr.get("assistant_lang", "?")
    by_lang[lang][key] += 1
    h = tr.get("assistant_hash")
    if h:
        b = by_hash[h]
        b[key] += 1
        if not b["lang"]: b["lang"] = lang
        if not b["bytes"]: b["bytes"] = tr.get("assistant_bytes", 0)
        if not b["head"]: b["head"] = tr.get("assistant_head", "")[:80]
        b["sessions"].add(tr["session"])
    by_preflight[tr.get("preflight_level", "?")] += 1
    by_signal[tr.get("signal", "?")] += 1

# ── winners (best L2/L1 ratio, min 3 trials) ──
winners = []
losers = []
for h, v in by_hash.items():
    total = v["L0"] + v["L1"] + v["L2"]
    if total < 3: continue
    v2 = {k: v[k] for k in ("L0","L1","L2")}
    v2["hash"] = h
    v2["lang"] = v["lang"]
    v2["bytes"] = v["bytes"]
    v2["head"] = v["head"]
    v2["sessions"] = len(v["sessions"])
    v2["total"] = total
    v2["ratio"] = v["L2"] / total if total else 0
    winners.append(v2)
    losers.append(v2)

winners.sort(key=lambda x: (-x["ratio"], -x["total"]))
losers.sort(key=lambda x: (x["ratio"], -x["total"]))

# ── write outputs ──
summary = {
    "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "elapsed_s": round(elapsed, 1),
    "totals": totals,
    "sessions_scored": scored,
    "sessions_skipped_excluded": skipped_excl,
    "sessions_skipped_short": skipped_short,
    "sessions_errored": errors,
    "unique_assistant_blocks": len(by_hash),
    "by_lang": {k: dict(v) for k, v in by_lang.items()},
    "by_preflight": dict(by_preflight),
    "by_signal": dict(by_signal),
    "top_candidates": winners[:30],
    "bottom_candidates": losers[:20],
}
OUT_TOT.write_text(json.dumps(summary, indent=2, default=str))

# append trials to jsonl (truncate first to keep it bounded)
with OUT_TRI.open("w") as f:
    for tr in all_trials:
        f.write(json.dumps(tr, default=str, ensure_ascii=False) + "\n")

# ── print report ──
log()
log("═" * 68)
log(f"  MVT 3L0 — full corpus run  {summary['generated']}")
log("═" * 68)
log(f"  sessions scored:      {scored:>5d}")
log(f"  sessions excluded:    {skipped_excl:>5d}  (personal/test/archive)")
log(f"  sessions too short:   {skipped_short:>5d}  (<4 msgs)")
log(f"  errors:               {errors:>5d}")
log(f"  unique blocks:        {len(by_hash):>5d}")
log(f"  total trials:         {len(all_trials):>5d}")
log()
log(f"  L0 (error):    {totals['L0']:>6d}")
log(f"  L1 (partial):  {totals['L1']:>6d}")
log(f"  L2 (success):  {totals['L2']:>6d}")
log()
log("  by language (top 8):")
for lang, counts in sorted(by_lang.items(), key=lambda kv: -(kv[1]["L0"]+kv[1]["L1"]+kv[1]["L2"]))[:8]:
    tot = counts["L0"] + counts["L1"] + counts["L2"]
    log(f"    {lang:12s}  L0={counts['L0']:>4d}  L1={counts['L1']:>4d}  L2={counts['L2']:>4d}  total={tot:>5d}")
log()
log("  by preflight level:")
for lv, n in by_preflight.most_common():
    log(f"    {lv:6s} {n:>5d}")
log()
log("═" * 68)
log("  TOP CANDIDATES (L2-heavy, ≥3 trials)")
log("═" * 68)
for w in winners[:15]:
    log(f"  {w['hash']:18s} {w['lang']:8s} {w['bytes']:>5d}B  "
        f"L0={w['L0']:>2d} L1={w['L1']:>2d} L2={w['L2']:>2d}  ratio={w['ratio']:.2f}  {w['head'][:60]}")

log()
log("═" * 68)
log("  BOTTOM CANDIDATES (L0-heavy, ≥3 trials)")
log("═" * 68)
for w in losers[:10]:
    log(f"  {w['hash']:18s} {w['lang']:8s} {w['bytes']:>5d}B  "
        f"L0={w['L0']:>2d} L1={w['L1']:>2d} L2={w['L2']:>2d}  ratio={w['ratio']:.2f}  {w['head'][:60]}")

log()
log(f"  totals     → {OUT_TOT.relative_to(HOME)}")
log(f"  trials     → {OUT_TRI.relative_to(HOME)}")
log(f"  cache      → {CACHE.relative_to(HOME)}")
