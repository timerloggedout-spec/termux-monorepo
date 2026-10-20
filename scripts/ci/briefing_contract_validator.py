#!/usr/bin/env python3
"""Validate the machine-checkable contract for briefing JSON and source registry.

Standard-library only so the check runs on Linux, Termux, and offline hosts.
This validates structure and provenance fields; it does not verify external
claims, determine whether a source is authoritative, or infer target portability.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date as date_cls, datetime
from pathlib import Path
from urllib.parse import urlsplit

HORIZONS = {"H0", "H1", "H2", "H3"}
EVIDENCE_STATUSES = {"confirmed", "research", "attributed", "signal", "speculative", "disputed"}
CONFIDENCE = {"high", "medium", "low", "unknown"}
ITEM_FIELDS = {
    "headline", "horizon", "evidence_status", "summary", "why_it_matters",
    "opportunity_or_procurement", "monorepo_relevance", "sources", "confidence",
    "unresolved_questions", "image_query",
}

# Bolt optimization: Pre-sorted ITEM_FIELDS tuple avoids repeated sorting in validation loops
SORTED_ITEM_FIELDS: tuple[str, ...] = tuple(sorted(ITEM_FIELDS))
CONTRACT_PATHS = {
    "spec": "docs/briefing/DAILY-DIGEST-SPEC.md",
    "ingest": "docs/research/BRIEFING-INGEST.md",
    "procurement": "docs/research/FOSS-PROCUREMENT-MATRIX.md",
    "radar": "docs/research/FORESIGHT-RADAR.md",
    "source_registry": "config/foresight_digest_sources.json",
}
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_http_url(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith(("http://", "https://")):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def _utc_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not UTC_TIMESTAMP.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_briefing(data: object) -> list[str]:
    """Return stable, human-readable contract violations for a briefing object."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["briefing: expected a JSON object"]
    if not _is_nonempty_string(data.get("schema_version")):
        errors.append("briefing.schema_version: expected a non-empty string")
    date = data.get("briefing_date")
    if not isinstance(date, str):
        errors.append("briefing.briefing_date: expected YYYY-MM-DD")
    else:
        try:
            # Bolt optimization: Fast date parsing with date.fromisoformat instead of datetime.strptime
            if date_cls.fromisoformat(date).isoformat() != date:
                raise ValueError
        except ValueError:
            errors.append("briefing.briefing_date: expected valid YYYY-MM-DD")
    if not _utc_timestamp(data.get("generated_at")):
        errors.append("briefing.generated_at: expected UTC ISO-8601 timestamp ending in Z")
    contract = data.get("contract")
    if not isinstance(contract, dict):
        errors.append("briefing.contract: expected object of canonical contract paths")
    else:
        for key, expected in CONTRACT_PATHS.items():
            if contract.get(key) != expected:
                errors.append(f"briefing.contract.{key}: expected {expected!r}")
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 5:
        errors.append("briefing.items: expected 1 to 5 substantive items (do not pad)")
        return errors
    for index, item in enumerate(items):
        prefix = f"briefing.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: expected object")
            continue
        for field in SORTED_ITEM_FIELDS:
            if field not in item:
                errors.append(f"{prefix}.{field}: required field missing")
        for field in ("headline", "summary", "why_it_matters", "opportunity_or_procurement",
                      "monorepo_relevance", "image_query"):
            if field in item and not _is_nonempty_string(item[field]):
                errors.append(f"{prefix}.{field}: expected non-empty string")
        if item.get("horizon") not in HORIZONS:
            errors.append(f"{prefix}.horizon: expected one of {sorted(HORIZONS)}")
        if item.get("evidence_status") not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status: expected one of {sorted(EVIDENCE_STATUSES)}")
        if item.get("confidence") not in CONFIDENCE:
            errors.append(f"{prefix}.confidence: expected one of {sorted(CONFIDENCE)}")
        questions = item.get("unresolved_questions")
        if not isinstance(questions, list) or any(not _is_nonempty_string(q) for q in questions):
            errors.append(f"{prefix}.unresolved_questions: expected a list of non-empty strings")
        sources = item.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{prefix}.sources: expected at least one source")
        else:
            for source_index, source in enumerate(sources):
                source_prefix = f"{prefix}.sources[{source_index}]"
                if not isinstance(source, dict):
                    errors.append(f"{source_prefix}: expected object")
                    continue
                if not _is_http_url(source.get("url")):
                    errors.append(f"{source_prefix}.url: expected absolute HTTP(S) URL")
                if not _is_nonempty_string(source.get("source_type")):
                    errors.append(f"{source_prefix}.source_type: expected non-empty provenance type")
    return errors


def validate_registry(data: object) -> list[str]:
    """Return stable violations for the standing source registry."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry: expected a JSON object"]
    if data.get("schema_version") != 2:
        errors.append("registry.schema_version: expected integer 2")
    families = data.get("resource_families")
    if not isinstance(families, list) or not families:
        errors.append("registry.resource_families: expected non-empty list")
        return errors
    seen: set[str] = set()
    for index, family in enumerate(families):
        prefix = f"registry.resource_families[{index}]"
        if not isinstance(family, dict):
            errors.append(f"{prefix}: expected object")
            continue
        for field in ("id", "name", "role", "url"):
            if not _is_nonempty_string(family.get(field)):
                errors.append(f"{prefix}.{field}: expected non-empty string")
        identifier = family.get("id")
        if isinstance(identifier, str):
            if identifier in seen:
                errors.append(f"{prefix}.id: duplicate resource id {identifier!r}")
            seen.add(identifier)
        if not _is_http_url(family.get("url")):
            errors.append(f"{prefix}.url: expected absolute HTTP(S) URL")
    return errors


def _load(path: Path) -> object:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--briefing", type=Path, action="append", default=[],
                        help="briefing JSON to validate (repeatable)")
    parser.add_argument("--registry", type=Path,
                        help="source registry JSON to validate")
    args = parser.parse_args(argv)
    if not args.briefing and not args.registry:
        parser.error("provide --briefing and/or --registry")
    errors: list[str] = []
    for path in args.briefing:
        try:
            found = validate_briefing(_load(path))
            errors.extend(f"{path}: {error}" for error in found)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot read valid JSON: {exc}")
    if args.registry:
        try:
            found = validate_registry(_load(args.registry))
            errors.extend(f"{args.registry}: {error}" for error in found)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{args.registry}: cannot read valid JSON: {exc}")
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("Briefing contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
