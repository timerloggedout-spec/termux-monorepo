#!/usr/bin/env python3
"""Run observe-mode ML pipelines against a redacted snapshot."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml_pipelines.ingest.snapshot import load_snapshot
from ml_pipelines.pipelines.orchestrate import run_all


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=ROOT / "ml_pipelines/fixtures/ops-snapshot.json",
    )
    args = parser.parse_args()
    snap = load_snapshot(args.snapshot)
    envelope = run_all(snap.as_dict())
    json.dump(envelope, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
