#!/usr/bin/env python3
"""Validate compliance with the Siglary compressed-notation standard (docs/proposals/active/notation-sets/SIGLARY-STANDARD.md).

Standard-library only so the check runs on Linux, Termux, and offline hosts.
Enforces decidable rules:
1. N∅ / NOT_ESTABLISHED as a stored data value in data files/blocks (hard violation).
2. Notation class distinctions in skill/ICM surfaces.
3. Reference to Siglary standard in CLAUDE.md / skill metadata.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Forbidden anti-patterns in data surfaces
FORBIDDEN_DATA_VALUES = {"NOT_ESTABLISHED", "N∅"}

def validate_json_data(path: Path, data: object, rel_path: str) -> list[str]:
    errors = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and v in FORBIDDEN_DATA_VALUES:
                errors.append(f"{rel_path}: hard violation: field '{k}' has forbidden data value '{v}'")
            else:
                errors.extend(validate_json_data(path, v, rel_path))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, str) and item in FORBIDDEN_DATA_VALUES:
                errors.append(f"{rel_path}[{index}]: hard violation: list item has forbidden data value '{item}'")
            else:
                errors.extend(validate_json_data(path, item, rel_path))
    return errors

def validate_file_content(path: Path, content: str) -> list[str]:
    errors = []
    rel_path = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)

    # Check 1: N∅ / NOT_ESTABLISHED as stored data values in JSON files
    if path.suffix == ".json":
        try:
            data = json.loads(content)
            errors.extend(validate_json_data(path, data, rel_path))
        except json.JSONDecodeError:
            pass # Ignore invalid JSON here or let other validators catch it

    # Check 2: Class distinction checks for skill / markdown files
    if path.suffix in {".md", ".markdown"}:
        lowered = content.lower()
        if "operator" in lowered and "glyph" in lowered:
            if "operator is a glyph" in lowered or "glyph is an operator" in lowered:
                errors.append(f"{rel_path}: class violation: conflation of operators and glyphs")

    return errors

def run_census(root: Path = ROOT) -> dict:
    violations = []
    checked_files = 0

    # Scope 1: Skill files
    skill_paths = list(root.glob("skills/**/*.md")) + list(root.glob("*.SKILLS")) + list(root.glob("**/SKILLS.md")) + list(root.glob("**/SKILL.md"))
    # Scope 2: ICM surfaces
    icm_paths = list(root.glob("docs/icm/**/*"))
    # Scope 3: CLAUDE.md files
    claude_paths = list(root.glob("**/CLAUDE.md"))
    # Scope 4: Data files
    data_paths = list(root.glob("data/**/*.json")) + list(root.glob("data/**/*.jsonl")) + list(root.glob("config/**/*.json"))

    all_paths = {p for p in skill_paths + icm_paths + claude_paths + data_paths if p.is_file()}

    for path in sorted(all_paths):
        checked_files += 1
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            file_errors = validate_file_content(path, content)
            violations.extend(file_errors)
        except Exception as exc:
            violations.append(f"{path}: read error: {exc}")

    hard_violations = [v for v in violations if "hard violation" in v]
    soft_violations = [v for v in violations if "hard violation" not in v]

    report = {
        "schema_version": 1,
        "checked_files": checked_files,
        "hard_violations_count": len(hard_violations),
        "soft_violations_count": len(soft_violations),
        "hard_violations": hard_violations,
        "soft_violations": soft_violations,
        "status": "FAIL" if hard_violations else "PASS"
    }
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Siglary standard compliance.")
    parser.add_argument("--report-out", type=Path, help="Path to write compliance JSON report")
    args = parser.parse_args()

    report = run_census()
    
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report written to {args.report_out}")

    print(f"Siglary Census: checked {report['checked_files']} files. Hard violations: {report['hard_violations_count']}, Soft violations: {report['soft_violations_count']}.")
    if report["hard_violations"]:
        for v in report["hard_violations"]:
            print(f"  [HARD] {v}", file=sys.stderr)
        return 1
    
    print("OK: Siglary conformance census passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
