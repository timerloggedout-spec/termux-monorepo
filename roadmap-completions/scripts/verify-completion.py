#!/usr/bin/env python3
"""Validate a roadmap exercise evidence.json against the repository rule catalog.

The verifier checks submitted test-result metadata and evidence files. It does not
execute arbitrary exercise code or test commands.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def repo_file(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Evidence path must remain inside the repository: {value}")
    resolved = (root / candidate).resolve()
    resolved.relative_to(root.resolve())
    return resolved


def merge_rules(defaults: dict[str, Any], overrides: dict[str, Any]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for kind in ("code", "test", "documentation", "portfolio"):
        merged[kind] = {**defaults.get(kind, {}), **overrides.get(kind, {})}
    return merged


def validate(root: Path, roadmap: str, exercise: str) -> dict[str, Any]:
    root = root.resolve()
    rules_path = root / "roadmap-completions/config/verification-rules.yaml"
    if not rules_path.is_file():
        raise ValueError(f"Verification rules file is missing: {rules_path.relative_to(root)}")
    rules_doc = yaml.safe_load(rules_path.read_text(encoding="utf-8")) or {}
    roadmap_rules = rules_doc.get("roadmaps", {}).get(roadmap)
    if roadmap_rules is None:
        raise ValueError(f"Unknown roadmap in verification rules: {roadmap}")
    exercise_rules = roadmap_rules.get("exercises", {}).get(exercise)
    if exercise_rules is None:
        raise ValueError(f"Unknown exercise for roadmap {roadmap}: {exercise}")

    evidence_path = root / "roadmap-completions/roadmaps" / roadmap / "exercises" / exercise / "evidence.json"
    if not evidence_path.is_file():
        raise ValueError(f"Evidence file is missing: {evidence_path.relative_to(root)}")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("roadmap") != roadmap or evidence.get("exercise") != exercise:
        raise ValueError("Evidence roadmap/exercise identifiers must match the selected exercise.")
    if evidence.get("status") != "completed":
        raise ValueError("Evidence status must be 'completed'.")

    records = evidence.get("evidence")
    if not isinstance(records, list):
        raise ValueError("Evidence field must be a list of typed evidence records.")
    by_type: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("type"), str):
            by_type.setdefault(record["type"], []).append(record)

    merged = merge_rules(rules_doc.get("defaults", {}), exercise_rules.get("rules", {}))
    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(ok), "detail": detail})

    for kind, config in merged.items():
        required = bool(config.get("required", False))
        entries = by_type.get(kind, [])
        if required and not entries:
            add_check(kind, False, "Required evidence record is missing.")
            continue
        if not entries:
            add_check(kind, True, "Optional evidence omitted.")
            continue

        kind_results: list[str] = []
        kind_ok = True
        for index, record in enumerate(entries, start=1):
            raw_path = record.get("path")
            if not isinstance(raw_path, str) or not raw_path.strip():
                if kind == "portfolio" and isinstance(record.get("url"), str) and record["url"].startswith("https://github.com/"):
                    kind_results.append("GitHub portfolio URL recorded; remote contents require separate review.")
                    kind_ok = False
                else:
                    kind_results.append("Evidence record requires a repository-relative path.")
                    kind_ok = False
                continue
            try:
                path = repo_file(root, raw_path)
            except (ValueError, OSError) as error:
                kind_results.append(str(error))
                kind_ok = False
                continue
            if kind == "portfolio":
                if not path.is_dir():
                    kind_results.append(f"Portfolio directory is missing: {raw_path}")
                    kind_ok = False
                    continue
                required_files = config.get("required_files", [])
                missing = [name for name in required_files if not (path / name).exists()]
                file_count = sum(1 for item in path.rglob("*") if item.is_file())
                if missing or file_count < int(config.get("min_files", 0)):
                    kind_results.append(f"Portfolio files missing={missing}; file_count={file_count}.")
                    kind_ok = False
                else:
                    kind_results.append(f"Portfolio directory contains {file_count} files and required entries.")
                continue
            if not path.is_file():
                kind_results.append(f"Evidence file is missing: {raw_path}")
                kind_ok = False
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            if kind == "code":
                size = path.stat().st_size
                extensions = config.get("extensions", [])
                patterns = config.get("patterns", [])
                valid = size >= int(config.get("min_size", 0))
                valid = valid and (not extensions or path.suffix in extensions or path.name in extensions)
                missing_patterns = [pattern for pattern in patterns if pattern not in content]
                valid = valid and not missing_patterns
                kind_results.append(
                    f"{raw_path}: {size} bytes; missing patterns={missing_patterns}."
                )
                kind_ok = kind_ok and valid
            elif kind == "test":
                coverage = record.get("coverage")
                minimum = float(config.get("min_coverage", 0))
                passing = record.get("passing", True)
                valid = isinstance(coverage, (int, float)) and coverage >= minimum and passing is True
                kind_results.append(
                    f"{raw_path}: recorded coverage={coverage}; required={minimum}; passing={passing}."
                )
                kind_ok = kind_ok and valid
            elif kind == "documentation":
                words = re.findall(r"\b[\w'-]+\b", content)
                missing_sections = [
                    section for section in config.get("sections", [])
                    if not re.search(rf"(?im)^#+\s*{re.escape(section)}\s*$", content)
                ]
                valid = len(words) >= int(config.get("min_words", 0)) and not missing_sections
                kind_results.append(
                    f"{raw_path}: {len(words)} words; missing sections={missing_sections}."
                )
                kind_ok = kind_ok and valid

        add_check(kind, kind_ok, " ".join(kind_results))

    passed = sum(1 for check in checks if check["passed"])
    score = round((passed / len(checks)) * 100) if checks else 0
    return {
        "ok": all(check["passed"] for check in checks),
        "roadmap": roadmap,
        "exercise": exercise,
        "score": score,
        "verification_mode": "evidence-metadata-and-files",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roadmap", required=True)
    parser.add_argument("--exercise", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    try:
        report = validate(args.root, args.roadmap, args.exercise)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        report = {
            "ok": False,
            "roadmap": args.roadmap,
            "exercise": args.exercise,
            "score": 0,
            "verification_mode": "evidence-metadata-and-files",
            "checks": [{"name": "input", "passed": False, "detail": str(error)}],
        }
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.json_output:
        args.json_output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
