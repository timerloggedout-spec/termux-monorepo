"""retry — burst → ±30s rest → repeat, with learning from history."""

from .runtime import HOME  # noqa: F401

# ─── retry policy: burst → ±30s rest → repeat ────────────────────────
# Phase A: burst, escalating short waits (sub-second → 5s)
# Phase B: rest ~30s ± noise ± learned offset from prior successes
_BURST_WAITS = [0.3, 0.7, 1.5, 3.0, 5.0]
_REST_BASE = 30.0
_REST_JITTER = 15.0
_RATE_MARKERS = ("Messages too frequent", "too frequent", "rate limit", "please wait")


def _learned_offset() -> float:
    """Median of successful rest durations from last 20 samples."""
    import json as _j
    import statistics as _st
    p = HOME / ".deepcli" / "logs" / "retry_learning.jsonl"
    if not p.exists():
        return 0.0
    samples = []
    try:
        for line in p.read_text().splitlines()[-200:]:
            try:
                r = _j.loads(line)
                if r.get("outcome") == "success" and "rest_s" in r:
                    samples.append(float(r["rest_s"]))
            except Exception:
                continue
    except Exception:
        return 0.0
    if len(samples) < 5:
        return 0.0
    med = _st.median(samples[-20:])
    return max(-15.0, min(15.0, med - _REST_BASE))


def _record_retry(outcome: str, rest_s: float, attempt: int, kind: str):
    import json as _j
    import datetime as _dt
    p = HOME / ".deepcli" / "logs" / "retry_learning.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with p.open("a") as f:
            f.write(_j.dumps({
                "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                "outcome": outcome,
                "rest_s": round(rest_s, 2),
                "attempt": attempt,
                "kind": kind,
            }) + "\n")
    except Exception:
        pass


def _retry_plan(max_bursts: int = 4):
    """Yield (phase, wait_s, burst_i) sequences. burst of 5, rest, repeat."""
    import random as _r
    offset = _learned_offset()
    for burst_i in range(max_bursts):
        for w in _BURST_WAITS:
            yield ("burst", w, burst_i)
        if burst_i < max_bursts - 1:
            rest = _REST_BASE + _r.uniform(-_REST_JITTER, _REST_JITTER) + offset
            yield ("rest", max(5.0, rest), burst_i)
