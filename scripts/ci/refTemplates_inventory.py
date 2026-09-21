#!/usr/bin/env python3
"""Inventory refTemplates slots (00→∞). Assert metadata contracts; emit JSONL.

No network. Safe for CI path filter refTemplates/**.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "refTemplates"
SLOT_RE = re.compile(r"^(\d{2}|[0-9]+)_|^smods$")


def slots() -> list[Path]:
    if not REF.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(REF.iterdir()):
        if p.is_dir() and (SLOT_RE.match(p.name) or p.name in {"smods"}):
            out.append(p)
    return out


def inventory_entry(slot: Path) -> dict:
    children = [c.name for c in sorted(slot.iterdir()) if c.is_dir() or c.suffix in {".md", ".txt"}]
    research_children = []
    if slot.name.startswith("15_"):
        for c in sorted(slot.iterdir()):
            if not c.is_dir():
                continue
            source = c / "SOURCE.txt"
            readme = c / "README.md"
            research_children.append(
                {
                    "name": c.name,
                    "has_source": source.is_file(),
                    "has_readme": readme.is_file(),
                    "source_preview": source.read_text(encoding="utf-8").strip().splitlines()[0]
                    if source.is_file() and source.stat().st_size
                    else None,
                }
            )
    return {
        "slot": slot.name,
        "path": str(slot.relative_to(ROOT)),
        "entries": children,
        "research_children": research_children,
        "collected_at": datetime.now(UTC).isoformat(),
    }


def validate(entries: list[dict]) -> list[str]:
    failures: list[str] = []
    for e in entries:
        if e["slot"].startswith("15_"):
            for rc in e.get("research_children", []):
                if not rc.get("has_source"):
                    failures.append(f"{e['slot']}/{rc['name']}: missing SOURCE.txt")
                if not rc.get("has_readme"):
                    failures.append(f"{e['slot']}/{rc['name']}: missing README.md")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="JSONL output path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on contract failures")
    args = parser.parse_args()

    entries = [inventory_entry(s) for s in slots()]
    failures = validate(entries)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fh:
            for e in entries:
                fh.write(json.dumps(e, sort_keys=True) + "\n")
        print(f"OK: wrote {len(entries)} slot records → {args.output}")
    else:
        for e in entries:
            print(json.dumps(e, sort_keys=True))

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        if args.strict:
            return 1
    else:
        print(f"OK: validated {len(entries)} slots, 0 contract failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
