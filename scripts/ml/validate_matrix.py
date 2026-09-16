#!/usr/bin/env python3
"""Validate the Issue #175 operator matrix catalog."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml_pipelines.matrix.load import load_matrix
from ml_pipelines.matrix.validate import validate_matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=ROOT / "docs/ops/ISSUE-175-MATRIX.yaml",
    )
    args = parser.parse_args()
    doc = load_matrix(args.path)
    validate_matrix(doc)
    print("OK", args.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
