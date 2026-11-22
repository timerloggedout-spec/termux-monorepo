#!/usr/bin/env python3
"""Check issue-form and label-trigger discoverability against the canonical map."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = Path(".github/ISSUE_TEMPLATE")
WORKFLOW_DIR = Path(".github/workflows")
MAP_PATH = Path("docs/ops/GITHUB-ISSUE-INTAKE-MAP.md")


def read_text(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def template_frontmatter(path: Path, text: str) -> str:
    if path.suffix.lower() != ".md":
        return text
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    return match.group(1) if match else ""


def labels_for_template(path: Path, text: str) -> list[str]:
    frontmatter = template_frontmatter(path, text)
    match = re.search(r"(?m)^labels:\s*(.*?)\s*$", frontmatter)
    if not match:
        return []
    value = match.group(1).strip().strip("'").strip('"')
    value = value.strip("[]")
    return [item.strip().strip("'").strip('"') for item in value.split(",") if item.strip()]


def labeled_event_workflows(root: Path) -> list[str]:
    found: list[str] = []
    for path in sorted((root / WORKFLOW_DIR).glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        on_match = re.search(r"(?ms)^on:\s*\n(.*?)(?=^jobs:\s*$)", text)
        if not on_match:
            continue
        on_block = on_match.group(1)
        for event in ("issues", "pull_request"):
            event_match = re.search(
                rf"(?ms)^  {event}:\s*(.*?)(?=^  [A-Za-z0-9_-]+:\s*|\Z)",
                on_block,
            )
            if event_match and re.search(r"\blabeled\b", event_match.group(1)):
                found.append(path.name)
                break
    return found


def audit(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    template_dir = root / TEMPLATE_DIR
    templates = sorted(
        path for path in template_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml", ".md"}
    )
    map_file = root / MAP_PATH
    if not map_file.is_file():
        return [f"Canonical issue intake map is missing: {MAP_PATH}"]
    map_text = map_file.read_text(encoding="utf-8")

    for path in templates:
        relative = path.relative_to(root).as_posix()
        if path.name not in map_text:
            errors.append(f"Template is absent from the intake map: {relative}")
        for label in labels_for_template(path, path.read_text(encoding="utf-8")):
            if f"`{label}`" not in map_text:
                errors.append(f"Template label is absent from the intake map: {relative}: {label}")

    for workflow in labeled_event_workflows(root):
        if workflow not in map_text:
            errors.append(f"Labeled-event workflow is absent from the intake map: {workflow}")

    if not templates:
        errors.append(f"Issue template directory is empty: {TEMPLATE_DIR}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Run the read-only coverage audit")
    args = parser.parse_args()
    errors = audit(args.root.resolve())
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    template_count = sum(
        1 for path in (args.root / TEMPLATE_DIR).iterdir()
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml", ".md"}
    )
    trigger_count = len(labeled_event_workflows(args.root.resolve()))
    print(f"PASS: {template_count} issue templates and {trigger_count} labeled-event workflows are mapped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
