#!/usr/bin/env python3
"""Feed health snapshot emitter (DoE ruling 2026-11-02).

Materializes the pool feed's health leg into the routed-dispatch corpus:
append-only arm_state snapshots at experiments/doe/routed-dispatch/
feed-health.jsonl, sourced from the quota plane's joined feed
(ops/quota/swarm-feed.json), each stamped {source, vintage}.

Emission triggers:
  (a) change — the joined per-arm state hash differs from the last
      snapshot on file;
  (b) cycle — --force (the fan-out workflow runs one snapshot per
      dispatch cycle).
Selection basis stays reconstructible after the fact: registry/readings
mutate, so the snapshot is the citable basis; join-at-read stays the
live view.

Fail-soft: a missing/unreadable feed prints DEFER and exits 0.
Readings are carried verbatim from the feed; nothing is derived beyond
the state hash — selectability is policy (DoE/Scout), never computed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FEED_REL = "ops/quota/swarm-feed.json"
OUT_REL = "experiments/doe/routed-dispatch/feed-health.jsonl"
SCHEMA = "routed-dispatch/feed-health/v1"


def arm_state(provider_rec: dict) -> dict:
    census = provider_rec.get("census") or {}
    credits = census.get("credits") or {}
    population = provider_rec.get("population") or {}
    return {
        "provider": provider_rec.get("provider"),
        "population_state": population.get("state"),
        "live_verified": provider_rec.get("live_verified"),
        "census_verdict": census.get("verdict"),
        "flags": census.get("flags") or [],
        "balance": credits.get("available"),
    }


def build_snapshot(feed: dict, now: str) -> dict:
    arms = [arm_state(p) for p in feed.get("providers", [])]
    arms.sort(key=lambda a: a["provider"] or "")
    state_hash = hashlib.sha256(
        json.dumps(arms, sort_keys=True).encode()).hexdigest()
    return {
        "schema": SCHEMA,
        "at": now,
        "source": {
            "path": FEED_REL,
            "feed_schema": feed.get("schema"),
            "vintage": feed.get("generated_at"),
        },
        "state_hash": state_hash,
        "arms": arms,
    }


def last_hash(out_path: Path) -> str | None:
    if not out_path.exists():
        return None
    last = None
    for line in out_path.read_text().splitlines():
        if line.strip():
            last = line
    if last is None:
        return None
    try:
        return json.loads(last).get("state_hash")
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--force", action="store_true",
                    help="emit even when the joined state is unchanged (cycle trigger)")
    args = ap.parse_args()
    root = Path(args.root)
    feed_path = root / FEED_REL
    try:
        feed = json.loads(feed_path.read_text())
    except Exception as e:
        print(f"DEFER feed-health snapshot: cannot read {FEED_REL}: {e}")
        return 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    snap = build_snapshot(feed, now)
    out_path = root / OUT_REL
    if not args.force and last_hash(out_path) == snap["state_hash"]:
        print("feed-health snapshot: joined state unchanged; no emission")
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a") as fh:
        fh.write(json.dumps(snap, sort_keys=True) + "\n")
    print(f"feed-health snapshot emitted: {len(snap['arms'])} arms, "
          f"vintage {snap['source']['vintage']}, hash {snap['state_hash'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
