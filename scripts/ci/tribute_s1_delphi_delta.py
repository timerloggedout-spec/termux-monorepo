#!/usr/bin/env python3
"""Tribute System 1 -> Delphi: emit only CHANGED outcomes, one per thread.

The route job writes decisions JSONL (one decision per thread scan). This
module turns that into the `signal` input of ./.github/workflows/delphi-signal.yml
(event: tribute-outcome) with two guarantees:

  * deduped per thread: one signal per subject.url (the newest decision wins);
  * changed only: a thread whose (outcome, weight) equals the last emitted
    value in the state file is skipped, so a thread is re-emitted only when
    its outcome actually moves (e.g. changes_requested -> merged).

State is a small JSON map {thread_url: {"outcome", "weight", "at"}} kept on
the tribute-s1/backfill branch (state/delphi-emitted.json). At most --cap
signals go out per run (delphi-signal accepts <=200); the rest stay pending
and emit on the next run because they are not written into the new state.

Stdlib only, no network.

  python3 scripts/ci/tribute_s1_delphi_delta.py decisions.jsonl \
      --state prev-state.json --new-state new-state.json > signal.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CAP = 200


def read_jsonl(paths: list[str]) -> list[dict]:
    out = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def latest_per_thread(records: list[dict]) -> dict[str, dict]:
    """Newest decision per thread URL (records later in the input win)."""
    by: dict[str, dict] = {}
    for rec in records:
        url = ((rec.get("subject") or {}).get("url") or "").strip()
        if url and isinstance(rec.get("delphi_signal"), dict):
            by[url] = rec
    return by


def delta(records: list[dict], state: dict, cap: int = CAP, now: str | None = None) -> tuple[list[dict], dict]:
    """Return (signals, new_state). Deterministic: threads are processed in URL order."""
    now = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_state = dict(state or {})
    signals: list[dict] = []
    for url, rec in sorted(latest_per_thread(records).items()):
        sig = rec["delphi_signal"]
        outcome = str(sig.get("outcome") or "")
        weight = sig.get("weight")
        if not isinstance(weight, (int, float)):
            continue
        prev = (state or {}).get(url) or {}
        if prev.get("outcome") == outcome and prev.get("weight") == weight:
            continue
        if len(signals) >= cap:
            break  # pending: not written to state, emits next run
        item = {"surface": sig.get("surface") or "tribute-lane", "repo": sig.get("repo") or "",
                "outcome": outcome, "weight": weight, "key": url}
        signals.append(item)
        new_state[url] = {"outcome": outcome, "weight": weight, "at": now}
    return signals, new_state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--state", default="")
    ap.add_argument("--new-state", default="")
    ap.add_argument("--cap", type=int, default=CAP)
    a = ap.parse_args(argv)
    state = {}
    if a.state and Path(a.state).exists():
        try:
            state = json.loads(Path(a.state).read_text(encoding="utf-8")) or {}
        except json.JSONDecodeError:
            state = {}
    signals, new_state = delta(read_jsonl(a.inputs), state, cap=max(1, min(a.cap, CAP)))
    if a.new_state:
        Path(a.new_state).parent.mkdir(parents=True, exist_ok=True)
        Path(a.new_state).write_text(json.dumps(new_state, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"tribute-s1 delphi delta: {len(signals)} changed of {len(latest_per_thread(read_jsonl(a.inputs)))} threads; "
          f"state {len(state)} -> {len(new_state)}", file=sys.stderr)
    json.dump(signals, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
