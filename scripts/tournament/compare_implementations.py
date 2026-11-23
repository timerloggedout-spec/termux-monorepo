#!/usr/bin/env python3
"""Compare two tournament implementation versions from matched run receipts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "deepcli"))
from deepcli.observatory.implementation_competition import compare_implementations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipts", type=Path, help="JSON array of matched implementation receipts")
    parser.add_argument("--output", type=Path, help="optional report output path")
    args = parser.parse_args()
    try:
        payload = json.loads(args.receipts.read_text(encoding="utf-8"))
        receipts = payload["receipts"] if isinstance(payload, dict) else payload
        report = compare_implementations(receipts)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"comparison failed: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
