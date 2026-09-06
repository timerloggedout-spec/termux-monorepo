#!/usr/bin/env python3
"""Print a minesweeper table for the captured snapshot."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml_pipelines.eval.report import render_table
from ml_pipelines.ingest.snapshot import load_snapshot
from ml_pipelines.pipelines.pr_minesweeper import run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=ROOT / "ml_pipelines/fixtures/ops-snapshot.json",
    )
    args = parser.parse_args()
    result = run(load_snapshot(args.snapshot).as_dict())
    rows = result["classified"]
    print(
        render_table(
            rows,
            ["number", "disposition", "lane", "state", "changed_files", "title"],
        )
    )
    print("\nsummary:", result["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
