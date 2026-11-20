#!/usr/bin/env python3
"""Validate the CNS organ registry and architecture projections."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "cns-organ-registry/v1"
EVIDENCE_CLASSES = {"verified", "derived", "inferred", "candidate", "proposed"}
REQUIRED_ORGAN_FIELDS = {
    "id", "name", "plane", "status", "owner", "canonical_sources",
    "responsibilities", "authority_boundary", "evidence_class",
}
ORGAN_ID = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_organ_registry(registry: Any, root: Path) -> list[str]:
    """Return deterministic findings for the CNS organ registry."""
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["registry must be a mapping"]
    if registry.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    if not isinstance(registry.get("source_ref"), str) or not registry["source_ref"].strip():
        errors.append("source_ref must be a non-empty string")
    organs = registry.get("organs")
    if not isinstance(organs, list) or not organs:
        return errors + ["organs must be a non-empty list"]

    seen: set[str] = set()
    root_resolved = root.resolve()
    for index, organ in enumerate(organs):
        label = f"organs[{index}]"
        if not isinstance(organ, dict):
            errors.append(f"{label} must be a mapping")
            continue
        missing = sorted(REQUIRED_ORGAN_FIELDS - set(organ))
        if missing:
            errors.append(f"{label} missing required fields: {', '.join(missing)}")
        organ_id = organ.get("id")
        if not isinstance(organ_id, str) or not ORGAN_ID.fullmatch(organ_id):
            errors.append(f"{label} id must match {ORGAN_ID.pattern}")
        elif organ_id in seen:
            errors.append(f"duplicate organ id: {organ_id}")
        else:
            seen.add(organ_id)

        for field in ("name", "plane", "status", "owner", "authority_boundary"):
            value = organ.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label} {field} must be a non-empty string")

        evidence_class = organ.get("evidence_class")
        if evidence_class not in EVIDENCE_CLASSES:
            errors.append(f"{label} evidence_class must be one of {sorted(EVIDENCE_CLASSES)}")
        status = organ.get("status")
        if isinstance(status, str) and status.startswith("proposed") and evidence_class != "proposed":
            errors.append(f"{label} with proposed status must use evidence_class=proposed")

        responsibilities = organ.get("responsibilities")
        if not isinstance(responsibilities, list) or not responsibilities:
            errors.append(f"{label} responsibilities must be a non-empty list")
        elif any(not isinstance(item, str) or not item.strip() for item in responsibilities):
            errors.append(f"{label} responsibilities must contain non-empty strings")

        sources = organ.get("canonical_sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label} canonical_sources must be a non-empty list")
            continue
        for source in sources:
            if not isinstance(source, str) or not source.strip():
                errors.append(f"{label} canonical source must be a non-empty path")
                continue
            candidate = (root / source).resolve()
            if not candidate.is_relative_to(root_resolved):
                errors.append(f"{label} canonical source escapes repository root: {source}")
            elif not candidate.exists():
                errors.append(f"{label} missing canonical source: {source}")

        related_prs = organ.get("related_prs", [])
        if not isinstance(related_prs, list) or any(type(number) is not int or number <= 0 for number in related_prs):
            errors.append(f"{label} related_prs must contain positive integers")
    return errors


def validate_integration_map(content: str) -> list[str]:
    """Validate Mermaid structure and the four edge-evidence classifications."""
    errors: list[str] = []
    if not isinstance(content, str) or not content.strip():
        return ["integration map must be non-empty text"]
    if not re.search(r"```mermaid\s+flowchart\s+(?:TD|TB|LR|RL|BT)\b", content, re.IGNORECASE):
        errors.append("integration map requires a Mermaid flowchart block")
    legend = re.search(r"(?:legend|classification)[^\n]*", content, re.IGNORECASE)
    if not legend:
        errors.append("integration map requires an edge-classification legend")
    else:
        line = legend.group(0).lower()
        for classification in ("verified", "derived", "proposed", "unresolved"):
            if classification not in line:
                errors.append(f"integration map legend must include {classification}")
    return errors


def validate_authority_matrix(content: str) -> list[str]:
    """Validate the owner matrix's tabular shape and unique domain rows."""
    if not isinstance(content, str) or not content.strip():
        return ["authority matrix must be non-empty text"]
    errors: list[str] = []
    rows = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ["authority matrix requires a Markdown table"]
    header = [cell.lower() for cell in rows[0]]
    if len(header) < 4 or "domain" not in header[0] or "owner" not in header[1]:
        errors.append("authority matrix header requires Domain and Canonical owner columns")
    seen: set[str] = set()
    for index, cells in enumerate(rows[1:], 1):
        if len(cells) != len(header):
            errors.append(f"authority matrix row {index} has {len(cells)} columns; expected {len(header)}")
            continue
        domain, owner = cells[0], cells[1]
        if not domain or not owner:
            errors.append(f"authority matrix row {index} requires a domain and canonical owner")
        elif domain in seen:
            errors.append(f"duplicate authority domain: {domain}")
        else:
            seen.add(domain)
    if len(rows) < 2:
        errors.append("authority matrix requires at least one domain row")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--registry", default="docs/architecture/CNS-ORGAN-REGISTRY.yaml")
    parser.add_argument("--map", dest="map_path", default="docs/architecture/CNS-INTEGRATION-MAP.mmd")
    parser.add_argument("--authority", default="docs/architecture/CNS-AUTHORITY-MATRIX.md")
    args = parser.parse_args()
    try:
        import yaml
    except ImportError:
        print("FAIL: PyYAML is required; install pyyaml", file=sys.stderr)
        return 2

    errors: list[str] = []
    try:
        registry = yaml.safe_load((args.root / args.registry).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"registry load failed: {exc}")
    else:
        errors.extend(validate_organ_registry(registry, args.root))
    for path, validator in (
        (args.map_path, validate_integration_map),
        (args.authority, validate_authority_matrix),
    ):
        try:
            value = (args.root / path).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read {path}: {exc}")
        else:
            errors.extend(f"{path}: {item}" for item in validator(value))
    if errors:
        print("CNS architecture validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CNS architecture validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
