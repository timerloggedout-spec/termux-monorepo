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
METADATA_CHILD_SLOTS = {"19_Provider_Inference_Catalogs"}


def slots() -> list[Path]:
    if not REF.is_dir():
        return []
    return [
        path for path in sorted(REF.iterdir())
        if path.is_dir() and (SLOT_RE.match(path.name) or path.name == "smods")
    ]


def _children_with_metadata(slot: Path) -> list[dict]:
    records = []
    for child in sorted(slot.iterdir()):
        if not child.is_dir():
            continue
        source = child / "SOURCE.txt"
        readme = child / "README.md"
        metadata = child / "metadata.json"
        lines = source.read_text(encoding="utf-8").strip().splitlines() if source.is_file() else []
        records.append({
            "name": child.name,
            "has_source": source.is_file(),
            "has_readme": readme.is_file(),
            "has_metadata": metadata.is_file(),
            "source_preview": lines[0] if lines else None,
        })
    return records


def inventory_entry(slot: Path) -> dict:
    children = [
        child.name for child in sorted(slot.iterdir())
        if child.is_dir() or child.suffix in {".md", ".txt"}
    ]
    research_children = _children_with_metadata(slot) if slot.name.startswith("15_") else []
    metadata_children = _children_with_metadata(slot) if slot.name in METADATA_CHILD_SLOTS else []
    return {
        "slot": slot.name,
        "path": str(slot.relative_to(ROOT)),
        "entries": children,
        "research_children": research_children,
        "metadata_children": metadata_children,
        "collected_at": datetime.now(UTC).isoformat(),
    }


def validate(entries: list[dict]) -> list[str]:
    failures: list[str] = []
    for entry in entries:
        child_sets = []
        if entry["slot"].startswith("15_"):
            child_sets.append(entry.get("research_children", []))
        if entry["slot"] in METADATA_CHILD_SLOTS:
            child_sets.append(entry.get("metadata_children", []))
        for children in child_sets:
            for child in children:
                prefix = f"{entry['slot']}/{child['name']}"
                if not child.get("has_source"):
                    failures.append(f"{prefix}: missing SOURCE.txt")
                if not child.get("has_readme"):
                    failures.append(f"{prefix}: missing README.md")
                if entry["slot"] in METADATA_CHILD_SLOTS and not child.get("has_metadata"):
                    failures.append(f"{prefix}: missing metadata.json")
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
        print(f"OK: wrote {len(entries)} slot records → {args.output}")
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
