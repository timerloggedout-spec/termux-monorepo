#!/usr/bin/env python3
"""Search-window pacer - Event Audit finding F4 (search-surface
burst, event census-2026-11-02T06:25:00Z: an involves: enumeration
hit the Search API secondary limit mid-census and lost its queue).

The standard (docs/ops/SEARCH-WINDOW-SCHEDULING.md):
1. BATCH - a census never fans out one query per actor when a
   window pull answers it: one query over the window
   (repo + updated range), paginated, with attribution joined
   locally. Per-key queries are the fallback, still paced.
2. PACE - the Search bucket is 30 requests/min and carries
   secondary limits on top: token-bucket pacing at a configurable
   rate (default 24/min, headroom under the cap), and on a
   403/429 secondary response the pacer backs off to the reset
   the API names (Retry-After / X-RateLimit-Reset) - it never
   retries inside the window.
3. CHECKPOINT - every completed unit is watermarked to a JSON
   checkpoint file as it lands; a cut (limit, crash, kill) resumes
   from the watermark instead of losing or repeating the queue.

This module is the reusable machinery: `Pacer` (pacing + backoff),
`Checkpoint` (watermarks), `plan_window_pull` / `plan_per_key`
(batch planners). Runners (e.g. the Registry lane's censuses) own
their query semantics; the pacer owns the window discipline.
Consolidated-interaction pattern throughout: few, planned calls -
never open loops. stdlib only.

CLI: python3 scripts/quota_search_pacer.py plan \
         --repo owner/repo --actors a,b,c [--per-page 100]
     prints the window-pull plan + the paced schedule estimate.
"""
import argparse
import json
import time
from pathlib import Path


class Pacer:
    """Token-bucket pacer for the GitHub Search window."""

    def __init__(self, rate_per_min=24, clock=time.monotonic,
                 sleep=time.sleep):
        self.min_interval = 60.0 / float(rate_per_min)
        self._clock = clock
        self._sleep = sleep
        self._next_ok = 0.0
        self.calls = 0

    def wait(self):
        now = self._clock()
        if now < self._next_ok:
            self._sleep(self._next_ok - now)
        self._next_ok = self._clock() + self.min_interval
        self.calls += 1

    def backoff(self, retry_after=None, reset_epoch=None):
        """Secondary-limit hit: sleep until the API's named reset.
        Returns the seconds waited. Never retries inside a window
        the API has closed."""
        now = time.time()
        delay = 60.0
        if retry_after:
            delay = float(retry_after)
        elif reset_epoch:
            delay = max(1.0, float(reset_epoch) - now)
        self._sleep(delay)
        self._next_ok = self._clock() + self.min_interval
        return delay


class Checkpoint:
    """JSON watermark: {done: [unit keys], updated_at, meta}.
    Saved after every unit; resume = skip done units."""

    def __init__(self, path):
        self.path = Path(path)
        self.done = []
        self.meta = {}
        if self.path.exists():
            d = json.loads(self.path.read_text())
            self.done = list(d.get("done", []))
            self.meta = dict(d.get("meta", {}))

    def is_done(self, unit):
        return unit in self.done

    def mark(self, unit):
        if unit not in self.done:
            self.done.append(unit)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(
            {"done": self.done, "meta": self.meta,
             "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                         time.gmtime())},
            indent=1) + "\n")

    def remaining(self, units):
        return [u for u in units if u not in self.done]


def plan_window_pull(repo, since, until, per_page=100,
                     est_results=None):
    """One query answers the whole census window; attribution is
    joined locally from the pulled items. Pages are the paced
    units; each page is a checkpoint unit."""
    q = f"repo:{repo} updated:{since}..{until}"
    pages = None
    if est_results is not None:
        pages = -(-est_results // per_page)
    return {"strategy": "window-pull", "query": q,
            "per_page": per_page, "est_pages": pages,
            "units": [f"page:{i}" for i in range(1, (pages or 0) + 1)],
            "note": "attribute involves/actors locally from pulled "
                    "items; one query, paginated inside the window "
                    "budget - replaces per-actor fan-out"}


def plan_per_key(repo, keys, qualifier="involves"):
    """Fallback when a window pull cannot answer: one paced query
    per key, each key a checkpoint unit (resume-safe)."""
    return {"strategy": "per-key",
            "queries": [f"repo:{repo} {qualifier}:{k}" for k in keys],
            "units": list(keys),
            "note": "paced by Pacer; checkpoint per key"}


def schedule_estimate(n_units, rate_per_min=24):
    return {"units": n_units, "rate_per_min": rate_per_min,
            "est_seconds": round(n_units * 60.0 / rate_per_min, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan"])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--actors", default="")
    ap.add_argument("--since", default="1970-01-01")
    ap.add_argument("--until", default="2999-12-31")
    ap.add_argument("--rate", type=int, default=24)
    a = ap.parse_args()
    actors = [x for x in a.actors.split(",") if x]
    plan = plan_window_pull(a.repo, a.since, a.until)
    plan["fallback"] = plan_per_key(a.repo, actors)
    plan["schedule"] = schedule_estimate(
        max(len(actors), 1), a.rate)
    print(json.dumps(plan, indent=1))


if __name__ == "__main__":
    main()
