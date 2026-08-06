#!/usr/bin/env python3
"""Print stale/blocked debates; exit 1 if any blocker or stale open debate."""
from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "docs" / "DEBATE" / "MATRIX.yaml"


def main() -> int:
    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    stale_after = int(data.get("stale_after_days") or 14)
    today = dt.date.today()
    bad = 0
    for d in data.get("debates") or []:
        if d.get("status") != "open":
            continue
        last = d.get("last_activity") or "1970-01-01"
        try:
            age = (today - dt.date.fromisoformat(str(last)[:10])).days
        except ValueError:
            age = 999
        if d.get("blocker"):
            print(f"BLOCKER {d['id']}: {d.get('blocker_note')}")
            bad += 1
        if age >= stale_after:
            print(f"STALE {d['id']}: {age}d (threshold {stale_after})")
            bad += 1
    if bad == 0:
        print("OK: no stale/blocked open debates")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
