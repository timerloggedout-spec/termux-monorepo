#!/usr/bin/env python3
"""Validate the curated Domain Atlas projection without network access."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "apps/historical-corpus-explorer/data/domain-atlas.json"
LAYERS = {"semantic", "operational"}
RELATIONSHIP_TYPES = {"PRODUCES", "PROJECTED_INTO", "EMITS_AND_MEASURES", "FEEDS_ANALYSIS", "GOVERNS", "CONSUMES", "SUPPORTS", "OPTIONAL_CONSUMER", "UNKNOWN"}
CLASSIFICATIONS = {"verified", "candidate", "unknown"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _validate_evidence(value: Any, label: str, source_sha: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label} must be an object"]
    errors = []
    for field in ("path", "claim", "url"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append(f"{label}.{field} must be a non-empty string")
    url = value.get("url")
    if isinstance(url, str) and url:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"{label}.url must be an absolute HTTPS URL")
        expected_prefix = f"https://github.com/timerloggedout-spec/termux-monorepo/blob/{source_sha}/"
        if not url.startswith(expected_prefix):
            errors.append(f"{label}.url must point to the pinned source SHA")
    return errors


def validate_domain_atlas(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["root must be an object"]
    if value.get("schema_version") != "1.0":
        errors.append("schema_version must equal 1.0")
    if value.get("projection") != "domain_atlas":
        errors.append("projection must equal domain_atlas")
    if not isinstance(value.get("source_ref"), str) or not value["source_ref"].strip():
        errors.append("source_ref must be a non-empty string")
    if not isinstance(value.get("source_sha"), str) or not SHA_RE.fullmatch(value["source_sha"]):
        errors.append("source_sha must be a full 40-character lowercase Git SHA")
    domains = value.get("domains")
    if not isinstance(domains, list) or not domains:
        errors.append("domains must be a non-empty array")
        domains = []
    domain_ids: set[str] = set()
    for index, domain in enumerate(domains):
        label = f"domains[{index}]"
        if not isinstance(domain, dict):
            errors.append(f"{label} must be an object")
            continue
        domain_id = domain.get("id")
        if not isinstance(domain_id, str) or not domain_id:
            errors.append(f"{label}.id must be a non-empty string")
        elif not ID_RE.fullmatch(domain_id):
            errors.append(f"{label}.id must be a lowercase slug")
        elif domain_id in domain_ids:
            errors.append(f"{label}.id duplicates {domain_id}")
        else:
            domain_ids.add(domain_id)
        for field in ("name", "role", "summary"):
            if not isinstance(domain.get(field), str) or not domain[field].strip():
                errors.append(f"{label}.{field} must be a non-empty string")
        sources = domain.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label}.sources must be a non-empty array")
            continue
        for source_index, source in enumerate(sources):
            errors.extend(_validate_evidence(source, f"{label}.sources[{source_index}]", value.get("source_sha", "")))
    relationships = value.get("relationships")
    if not isinstance(relationships, list):
        errors.append("relationships must be an array")
        relationships = []
    relationship_ids: set[str] = set()
    for index, edge in enumerate(relationships):
        label = f"relationships[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{label} must be an object")
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append(f"{label}.id must be a non-empty string")
        elif not ID_RE.fullmatch(edge_id):
            errors.append(f"{label}.id must be a lowercase slug")
        elif edge_id in relationship_ids:
            errors.append(f"{label}.id duplicates {edge_id}")
        else:
            relationship_ids.add(edge_id)
        for endpoint in ("source", "target"):
            if edge.get(endpoint) not in domain_ids:
                errors.append(f"{label}.{endpoint} does not resolve to a domain")
        if edge.get("type") not in RELATIONSHIP_TYPES:
            errors.append(f"{label}.type is unsupported")
        layers = edge.get("layers")
        if not isinstance(layers, list) or not layers or any(layer not in LAYERS for layer in layers):
            errors.append(f"{label}.layers must contain semantic and/or operational")
        classification = edge.get("classification")
        if classification not in CLASSIFICATIONS:
            errors.append(f"{label}.classification is unsupported")
        evidence = edge.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{label}.evidence must be an array")
            continue
        if classification == "verified" and not evidence:
            errors.append(f"{label}: verified relationships require evidence")
        for evidence_index, item in enumerate(evidence):
            errors.extend(_validate_evidence(item, f"{label}.evidence[{evidence_index}]", value.get("source_sha", "")))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args()
    try:
        value = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"domain-atlas validation failed: {exc}", file=sys.stderr)
        return 2
    errors = validate_domain_atlas(value)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status":"PASS","projection":value["projection"],"source_sha":value["source_sha"],"domains":len(value["domains"]),"relationships":len(value["relationships"]),"classification_counts":{status:sum(edge["classification"]==status for edge in value["relationships"]) for status in sorted(CLASSIFICATIONS)}},sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
