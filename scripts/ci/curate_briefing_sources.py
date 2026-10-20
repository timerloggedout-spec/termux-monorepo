#!/usr/bin/env python3
"""Curate cited URLs from daily briefs and evidence documents into deterministic JSONL.

Offline-only: this tool extracts references; it does not fetch, bless, or verify
claims. Each citation retains the document/item context that made the source
relevant. Repeated citations across different documents remain distinct.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
TRAILING = ".,;:!?)]}"
DEFAULT_DOCS = (
    "docs/ops/AGENT-TEAM-ORCHESTRATION.md",
    "docs/ops/AGENT-OBSERVABILITY-PRIORITY-DECISION.md",
    "docs/ops/SCOUT-MISSIONS.md",
    "docs/ops/FORESIGHT-EVIDENCE-SPINE.md",
    "docs/ops/AGENT-THROUGHPUT-METRICS.md",
    "docs/ops/BRIDGE-REDUNDANCY.md",
    "docs/ops/TERMUX-LIVE-BRIDGE.md",
    "docs/ops/ACTIONS-WORKFLOWS-MATRIX.md",
    "docs/ops/sessions/HINDSIGHT.md",
    # Provider/API evidence used by the current procurement and adapter lanes.
    "docs/ops/PROVIDER-BATCH-IMPLEMENTATION.md",
    "docs/ops/PROVIDER-SERVICE-EXPANSION.md",
    "docs/ops/PROVIDER-HITL.md",
    "docs/ops/FREE-LLM-PROVIDER-RECON.md",
    "docs/ops/PROVIDER-RESEARCH-COMPOUNDING.md",
    "docs/ops/GITHUB-FEEDBACK-API-DIAGNOSTICS.md",
    # Collaborator identity, execution and evidence contracts.
    "docs/ops/AGENT-MONIKERS.md",
    "docs/ops/AGENT-TEAM-ROSTER.md",
    "docs/ops/AGENT-EVIDENCE-SUBSTRATE.md",
    "docs/ops/BIUDL-EXECUTION-AND-PROVENANCE.md",
    "docs/ops/LANE-MATRIX.md",
    "docs/research/FOSS-PROCUREMENT-MATRIX.md",
    "docs/research/FORESIGHT-RADAR.md",
    "docs/research/BRIEFING-INGEST.md",
)


def clean_url(value: str) -> str:
    """Strip sentence punctuation without rewriting the cited URL."""
    return value.rstrip(TRAILING)


def is_http_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith(("http://", "https://")):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def citation_id(source_url: str, source_file: str, item_id: str | None, locator: str) -> str:
    material = "\\0".join((source_url, source_file, item_id or "", locator))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _record(source_url: str, source_file: str, locator: str, context: dict[str, Any],
            citation_text: str | None = None) -> dict[str, Any]:
    item_id = context.get("item_id")
    return {
        "schema_version": "briefing.citation.v1",
        "citation_id": citation_id(source_url, source_file, item_id, locator),
        "source_url": source_url,
        "source_file": source_file,
        "source_locator": locator,
        "citation_text": citation_text,
        "item_id": item_id,
        "item_headline": context.get("item_headline"),
        "source_type": context.get("source_type"),
        "observed_at": context.get("observed_at"),
        "published": context.get("published"),
        "version_or_commit": context.get("version_or_commit") or context.get("version"),
        "evidence_status": context.get("evidence_status"),
        "horizon": context.get("horizon"),
        "confidence": context.get("confidence"),
    }


def _json_citations(value: Any, source_file: str, locator: str = "$",
                    inherited: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    context = dict(inherited or {})
    if isinstance(value, dict):
        for key in ("id", "item_id", "resource_id", "signal_id"):
            if isinstance(value.get(key), (str, int)) and str(value[key]).strip():
                context.setdefault("item_id", str(value[key]))
                break
        for key in ("headline", "title", "name"):
            if isinstance(value.get(key), str) and value[key].strip():
                context.setdefault("item_headline", value[key].strip())
                break
        for key in ("source_type", "observed_at", "published", "version", "version_or_commit",
                    "evidence_status", "horizon", "confidence", "generated_at", "briefing_date"):
            if value.get(key) is not None:
                context.setdefault(key, value[key])
        if context.get("observed_at") is None:
            context["observed_at"] = context.get("generated_at") or context.get("briefing_date")
        for key in ("canonical_source", "canonical_url", "url", "source_url"):
            candidate = value.get(key)
            if is_http_url(candidate):
                source_type = value.get("source_type") or value.get("type")
                local_context = dict(context)
                if source_type:
                    local_context["source_type"] = source_type
                records.append(_record(candidate, source_file, f"{locator}.{key}", local_context,
                                       value.get("title") if isinstance(value.get("title"), str) else None))
        for key, child in value.items():
            if key in {"canonical_source", "canonical_url", "url", "source_url"}:
                continue
            records.extend(_json_citations(child, source_file, f"{locator}.{key}", context))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            records.extend(_json_citations(child, source_file, f"{locator}[{index}]", context))
    elif isinstance(value, str) and is_http_url(value):
        records.append(_record(value, source_file, locator, context))
    return records


def _markdown_citations(text: str, source_file: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    heading = None
    # Bolt optimization: Pre-compiled HEADING_RE and "http" substring fast-path guard
    # bypass link extraction loops on non-link prose lines.
    for line_number, line in enumerate(text.splitlines(), 1):
        match = HEADING_RE.match(line)
        if match:
            heading = match.group(1).strip()
        if "http" not in line and "HTTP" not in line:
            continue
        context = {"item_headline": heading}
        # Markdown links preserve link text; the raw URL pass adds only URLs
        # not already covered on this line.
        seen: set[str] = set()
        for link_text, raw_url in MARKDOWN_LINK_RE.findall(line):
            url = clean_url(raw_url)
            if is_http_url(url):
                records.append(_record(url, source_file, f"L{line_number}", context, link_text.strip()))
                seen.add(url)
        for raw_url in URL_RE.findall(line):
            url = clean_url(raw_url)
            if is_http_url(url) and url not in seen:
                records.append(_record(url, source_file, f"L{line_number}", context))
                seen.add(url)
    return records


def discover_inputs(root: Path) -> list[Path]:
    """Return the bounded briefing/evidence corpus plus explicitly curated SSOTs."""
    paths: set[Path] = set()
    for pattern in (
        "docs/briefing/**/*.md", "docs/briefing/**/*.json",
        "data/briefing/briefings/**/*.json", "data/briefing/*.jsonl",
    ):
        paths.update(path for path in root.glob(pattern) if path.is_file())
    paths.update(root / item for item in DEFAULT_DOCS if (root / item).is_file())
    excluded = {"source-citations.jsonl", "SOURCE-CITATION-INDEX.md"}
    return sorted(path for path in paths if path.name not in excluded)


def curate(paths: Iterable[Path], root: Path) -> list[dict[str, Any]]:
    """Extract citations, keeping source document and item provenance."""
    records: list[dict[str, Any]] = []
    for path in sorted(set(paths)):
        try:
            relative = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            raise ValueError(f"cannot read source document {path}: {exc}") from exc
        if path.suffix.lower() in {".md", ".markdown"}:
            records.extend(_markdown_citations(text, relative))
        elif path.suffix.lower() == ".jsonl":
            for line_number, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{relative}:L{line_number}: invalid JSONL: {exc}") from exc
                records.extend(_json_citations(parsed, relative, f"L{line_number}"))
        elif path.suffix.lower() == ".json":
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{relative}: invalid JSON: {exc}") from exc
            records.extend(_json_citations(parsed, relative))
    # Stable exact-instance deduplication; same URL cited by another item/file stays.
    unique = {row["citation_id"]: row for row in records}
    return [unique[key] for key in sorted(unique)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--input", type=Path, action="append", default=[],
                        help="explicit source file (repeatable); defaults to the curated corpus")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    paths = [path if path.is_absolute() else root / path for path in args.input]
    if not paths:
        paths = discover_inputs(root)
    try:
        records = curate(paths, root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Curated {len(records)} citation instances from {len(paths)} source documents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
