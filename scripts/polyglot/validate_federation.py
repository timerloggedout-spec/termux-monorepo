#!/usr/bin/env python3
"""Deterministic, stdlib-only validator for PolyGlot federation examples."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs" / "integrations" / "polyglot"
ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
REQUIRED = {
    "capability": {"schema_version", "capability_id", "name", "domain", "description", "status", "provenance"},
    "technology_target": {"schema_version", "target_id", "name", "domain", "target_kind", "lifecycle_state", "sources", "specialist"},
    "mapping": {"schema_version", "mapping_id", "capability_id", "target_id", "mapping_kind", "status", "coverage", "loss_profile"},
    "benchmark_result": {"schema_version", "result_id", "domain", "target_id", "capability_ids", "benchmark", "baseline", "environment", "measurements", "correctness", "provenance"},
}

def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: {exc}") from exc

def validate() -> list[str]:
    errors: list[str] = []
    examples = BASE / "examples"
    capability = load(examples / "capability.json")
    targets_doc = load(examples / "technology-targets.json")
    if not REQUIRED["capability"] <= set(capability):
        errors.append("capability example: required fields missing")
    if capability.get("schema_version") != "1.0.0":
        errors.append("capability example: unsupported schema_version")
    if not ID_RE.fullmatch(str(capability.get("capability_id", ""))):
        errors.append("capability example: invalid capability_id")
    if not isinstance(capability.get("provenance"), dict) or not capability["provenance"].get("source_uri"):
        errors.append("capability example: provenance.source_uri required")
    targets = targets_doc.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("technology targets: targets must be a non-empty array")
        targets = []
    seen: set[str] = set()
    for index, target in enumerate(targets):
        missing = REQUIRED["technology_target"] - set(target)
        if missing:
            errors.append(f"technology target {index}: missing {', '.join(sorted(missing))}")
        target_id = target.get("target_id", "")
        if not ID_RE.fullmatch(str(target_id)):
            errors.append(f"technology target {index}: invalid target_id {target_id!r}")
        if target_id in seen:
            errors.append(f"technology targets: duplicate target_id {target_id}")
        seen.add(target_id)
        if target.get("schema_version", "1.0.0") != "1.0.0":
            errors.append(f"technology target {target_id}: unsupported schema_version")
        if not isinstance(target.get("sources"), list) or not target["sources"]:
            errors.append(f"technology target {target_id}: at least one source required")
        for source in target.get("sources", []):
            if not str(source.get("uri", "")).startswith(("https://", "http://")):
                errors.append(f"technology target {target_id}: source URI must be HTTP(S)")
    return errors

def main() -> int:
    global ROOT, BASE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    args = parser.parse_args()
    ROOT = args.root.resolve()
    BASE = ROOT / "docs" / "integrations" / "polyglot"
    try:
        errors = validate()
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: PolyGlot federation examples and cross-record identifiers are structurally valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
