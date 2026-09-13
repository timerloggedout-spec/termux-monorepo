#!/usr/bin/env python3
"""Validate a JSONL fixture. Never talks to the network."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from probes.manus.harvester.normalize import dedup_events, normalize_event


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixture",
        type=Path,
        default=ROOT / "probes/manus/fixtures/sample-session.jsonl",
    )
    args = parser.parse_args()
    events = []
    for line in args.fixture.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        events.append(normalize_event(json.loads(line)))
    events = dedup_events(events)
    json.dump({"count": len(events), "observe_only": True}, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
