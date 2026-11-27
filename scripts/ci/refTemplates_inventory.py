#!/usr/bin/env python3
"""Inventory refTemplates slots and validate metadata contracts.

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
SLOT_RE = re.compile(r"^([0-9]{2}|[0-9]+)_|^smods$")
REFERENCE_CATEGORIES = {
    "05_Safety_Observability",
    "11_Evaluation_Quality",
    "15_Research_Repo_Templates",
}


def slots() -> list[Path]:
    if not REF.is_dir():
        return []
    return [
        path for path in sorted(REF.iterdir())
        if path.is_dir() and (SLOT_RE.match(path.name) or path.name == "smods")
    ]


def child_metadata(parent: Path) -> list[dict]:
    rows = []
    for child in sorted(parent.iterdir()):
        if not child.is_dir():
            continue
        source = child / "SOURCE.txt"
        readme = child / "README.md"
        preview = None
        if source.is_file() and source.stat().st_size:
            preview = source.read_text(encoding="utf-8").strip().splitlines()[0]
        rows.append({
            "name": child.name,
            "has_source": source.is_file(),
            "has_readme": readme.is_file(),
            "source_preview": preview,
        })
    return rows


def inventory_entry(slot: Path) -> dict:
    children = [
        child.name for child in sorted(slot.iterdir())
        if child.is_dir() or child.suffix in {".md", ".txt"}
    ]
    references = child_metadata(slot) if slot.name in REFERENCE_CATEGORIES else []
    return {
        "slot": slot.name,
        "path": str(slot.relative_to(ROOT)),
        "entries": children,
        "reference_children": references,
        # Keep the existing scoring consumer stable.
        "research_children": references if slot.name == "15_Research_Repo_Templates" else [],
        "collected_at": datetime.now(UTC).isoformat(),
    }


def validate(entries: list[dict]) -> list[str]:
    failures: list[str] = []
    for entry in entries:
        if entry["slot"] not in REFERENCE_CATEGORIES:
            continue
        for child in entry.get("reference_children", []):
            prefix = f"{entry['slot']}/{child['name']}"
            if not child.get("has_source"):
                failures.append(f"{prefix}: missing SOURCE.txt")
            if not child.get("has_readme"):
                failures.append(f"{prefix}: missing README.md")
            if not child.get("source_preview"):
                failures.append(f"{prefix}: SOURCE.txt is empty")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="JSONL output path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on contract failures")
    args = parser.parse_args()

    entries = [inventory_entry(slot) for slot in slots()]
    failures = validate(entries)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")
        print(f"OK: wrote {len(entries)} slot records -> {args.output}")
    else:
        for entry in entries:
            print(json.dumps(entry, sort_keys=True))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        if args.strict:
            return 1
    else:
        print(f"OK: validated {len(entries)} slots, 0 contract failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
