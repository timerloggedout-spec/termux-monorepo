#!/usr/bin/env python3
"""Inventory refTemplates slots and category candidates; emit deterministic JSONL.

Use local repository metadata. Keep research-template contracts separate from capability metadata.
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
CAPABILITY_SLOT_RE = re.compile(r"^(0[1-9]|1[0-4])_")
METADATA_NAMES = {"metadata", "metadata.json", "metadata.yaml", "metadata.yml", "metadata.txt"}


def slots() -> list[Path]:
    if not REF.is_dir():
        return []
    return sorted(
        p for p in REF.iterdir()
        if p.is_dir() and (SLOT_RE.match(p.name) or p.name == "smods")
    )


def _first_line(path: Path) -> str | None:
    if not path.is_file() or path.stat().st_size == 0:
        return None
    content = path.read_text(encoding="utf-8").strip()
    return content.splitlines()[0] if content else None


def capability_child_entry(slot: Path, child: Path) -> dict:
    source = child / "SOURCE.txt"
    readme = child / "README.md"
    metadata_files = sorted(
        p.name for p in child.iterdir()
        if p.is_file() and (p.name in METADATA_NAMES or p.name == "SOURCE.txt")
    )
    preview = _first_line(source)
    if preview is None:
        for name in sorted(METADATA_NAMES):
            preview = _first_line(child / name)
            if preview:
                break
    if source.is_file():
        provenance_state = "source_recorded"
    elif metadata_files or readme.is_file():
        provenance_state = "metadata_only"
    else:
        provenance_state = "unattributed"
    return {
        "name": child.name,
        "category": slot.name,
        "path": str(child.relative_to(ROOT)),
        "has_source": source.is_file(),
        "has_readme": readme.is_file(),
        "metadata_files": metadata_files,
        "source_preview": preview,
        "provenance_state": provenance_state,
        "candidate_state": "discovered",
    }


def inventory_entry(slot: Path) -> dict:
    children = [
        c.name for c in sorted(slot.iterdir())
        if c.is_dir() or c.suffix in {".md", ".txt"}
    ]
    research_children = []
    candidate_children = []
    if slot.name.startswith("15_"):
        for child in sorted(slot.iterdir()):
            if not child.is_dir():
                continue
            source = child / "SOURCE.txt"
            readme = child / "README.md"
            research_children.append({
                "name": child.name,
                "has_source": source.is_file(),
                "has_readme": readme.is_file(),
                "source_preview": _first_line(source),
            })
    elif CAPABILITY_SLOT_RE.match(slot.name):
        for child in sorted(slot.iterdir()):
            if child.is_dir():
                candidate_children.append(capability_child_entry(slot, child))
    return {
        "slot": slot.name,
        "path": str(slot.relative_to(ROOT)),
        "entries": children,
        "research_children": research_children,
        "candidate_children": candidate_children,
        "candidate_count": len(candidate_children),
        "collected_at": datetime.now(UTC).isoformat(),
    }


def validate(entries: list[dict]) -> list[str]:
    failures: list[str] = []
    for entry in entries:
        if entry["slot"].startswith("15_"):
            for child in entry.get("research_children", []):
                if not child.get("has_source"):
                    failures.append(f"{entry['slot']}/{child['name']}: missing SOURCE.txt")
                if not child.get("has_readme"):
                    failures.append(f"{entry['slot']}/{child['name']}: missing README.md")
        for child in entry.get("candidate_children", []):
            if child.get("provenance_state") not in {
                "source_recorded", "metadata_only", "unattributed"
            }:
                failures.append(
                    f"{entry['slot']}/{child.get('name', '<unknown>')}: invalid provenance_state"
                )
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
        candidate_count = sum(entry["candidate_count"] for entry in entries)
        print(
            f"OK: validated {len(entries)} slots, {candidate_count} capability candidates, "
            "0 contract failures"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
