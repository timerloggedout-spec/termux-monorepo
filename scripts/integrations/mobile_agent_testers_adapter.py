#!/usr/bin/env python3
"""Normalize locally collected Mobile Agent Testers findings into Integration Intelligence JSONL.

The collector intentionally reads only findings.json metadata. Raw reports, screenshots,
agent transcripts, and decrypted bundles remain on the trusted local machine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

INTEGRATION_ID = "mobile-agent-testers"
ADAPTER_VERSION = "1.0.0"
SEVERITIES = {"blocker", "major", "minor", "cosmetic"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\w)\+?\d[\d(). -]{7,}\d(?!\w)")
TOKEN_RE = re.compile(
    r"\b(?:bearer|token|api[_ -]?key|secret|password)\s*[:=]?\s*[A-Za-z0-9._~+/=-]{8,}",
    re.I,
)
SECRET_VALUE_RE = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
PERSONA_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
SHA_RE = re.compile(r"^[0-9a-f]{7,64}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


def safe_text(value: Any, limit: int) -> str:
    """Bound and redact text fields before they enter the canonical event stream."""
    text = CONTROL_RE.sub(" ", str(value or ""))
    text = EMAIL_RE.sub("[redacted-email]", text)
    text = PHONE_RE.sub("[redacted-phone]", text)
    text = TOKEN_RE.sub("[redacted-secret]", text)
    text = SECRET_VALUE_RE.sub("[redacted-secret]", text)
    return " ".join(text.split())[:limit]


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finding_files(run_dir: Path) -> Iterable[Path]:
    # Mirrors the provider collector layout: <artifact>/results/<persona>/findings.json.
    yield from sorted(run_dir.glob("*/results/*/findings.json"))


def make_event(
    *,
    run_id: str,
    repository: str,
    commit: str | None,
    persona: str,
    issue_index: int,
    issue: dict[str, Any],
    evidence_digest: str,
    started_at: str | None,
    completed_at: str | None,
    execution_status: str,
) -> dict[str, Any] | None:
    title = safe_text(issue.get("title"), 240)
    if not title:
        return None
    severity = str(issue.get("severity") or "").strip().lower()
    if severity not in SEVERITIES:
        severity = "unknown"
    screen = safe_text(issue.get("screen"), 120)
    stable_material = "|".join((run_id, persona, str(issue_index), title.lower()))
    stable_hash = hashlib.sha256(stable_material.encode("utf-8")).hexdigest()[:24]
    event_id = f"mat-{stable_hash}"
    event: dict[str, Any] = {
        "schema_version": "1.0.0",
        "event_id": event_id,
        "integration_id": INTEGRATION_ID,
        "event_type": "mobile_test.finding",
        "source": {
            "repository": repository,
            "commit_sha": commit,
            "pull_request": None,
            "workflow_run_id": None,
            "provider_request_id": run_id,
        },
        "execution": {
            "status": execution_status,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_ms": None,
        },
        "outcome": {
            "state": "observed",
            "summary": f"AI-reported {severity} finding: {title}",
            "confidence": "unknown",
        },
        "evidence": {
            "artifact_refs": [f"sha256:{evidence_digest}"],
            "validation_status": "pending",
            "validator": None,
        },
        "provenance": {
            "provider": "Mobile Agent Testers",
            "capture_method": f"encrypted GitHub Actions artifact; locally decrypted; persona={persona}",
            "attribution": "provider_reported",
            "model_id": None,
            "adapter_version": ADAPTER_VERSION,
        },
        "idempotency_key": f"{INTEGRATION_ID}:{run_id}:{persona}:{stable_hash}",
        "privacy": {
            "classification": "confidential",
            "contains_raw_prompt": False,
            "contains_secret": False,
            "redaction_applied": True,
        },
    }
    if screen:
        event["outcome"]["summary"] += f" (screen: {screen})"
    return event


def normalize(
    run_dir: Path,
    *,
    run_id: str,
    repository: str,
    commit: str | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
    execution_status: str = "unknown",
) -> tuple[list[dict[str, Any]], list[str], int, set[str]]:
    events: list[dict[str, Any]] = []
    diagnostics: list[str] = []
    valid_files = 0
    valid_personas: set[str] = set()
    for path in finding_files(run_dir):
        persona = path.parent.name
        if not PERSONA_RE.fullmatch(persona):
            diagnostics.append(f"skip unsafe persona directory: {path.parent}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            diagnostics.append(f"skip malformed findings file {path}: {type(exc).__name__}")
            continue
        if not isinstance(data, dict):
            diagnostics.append(f"skip non-object findings file: {path}")
            continue
        issues = data.get("issues")
        if not isinstance(issues, list):
            diagnostics.append(f"skip findings without issue list: {path}")
            continue
        try:
            source_digest = digest_file(path)
        except OSError as exc:
            diagnostics.append(f"skip unreadable findings file {path}: {type(exc).__name__}")
            continue
        if not issues:
            valid_files += 1
            valid_personas.add(persona)
            continue
        file_events: list[dict[str, Any]] = []
        for index, issue in enumerate(issues):
            if not isinstance(issue, dict):
                diagnostics.append(f"skip non-object issue {index} in {path}")
                continue
            event = make_event(
                run_id=run_id,
                repository=repository,
                commit=commit,
                persona=persona,
                issue_index=index,
                issue=issue,
                evidence_digest=source_digest,
                started_at=started_at,
                completed_at=completed_at,
                execution_status=execution_status,
            )
            if event is None:
                diagnostics.append(f"skip issue with empty title {index} in {path}")
                continue
            file_events.append(event)
        if file_events:
            valid_files += 1
            valid_personas.add(persona)
            events.extend(file_events)
        else:
            diagnostics.append(f"skip findings file without valid issue entries: {path}")
    return events, diagnostics, valid_files, valid_personas


def iso_datetime(value: str) -> str:
    """Accept only timezone-aware ISO-8601 timestamps for schema date-time fields."""
    if not DATETIME_RE.fullmatch(value):
        raise argparse.ArgumentTypeError("timestamp must include seconds and timezone in ISO-8601 form")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("timestamp must include a timezone")
    return value


def parse_personas(value: str) -> set[str]:
    personas = [item.strip() for item in value.split(",") if item.strip()]
    if not personas or len(personas) != len(set(personas)) or any(
        not PERSONA_RE.fullmatch(persona) for persona in personas
    ):
        raise argparse.ArgumentTypeError("expected a comma-separated list of unique persona IDs")
    return set(personas)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path, help="trusted, locally decrypted run directory")
    parser.add_argument("--run-id", required=True, help="immutable provider workflow run ID")
    parser.add_argument("--expected-personas", required=True, type=parse_personas, help="comma-separated persona IDs dispatched for this run")
    parser.add_argument("--repository", default="timerloggedout-spec/termux-monorepo")
    parser.add_argument("--commit", help="tested source commit SHA")
    parser.add_argument("--started-at", type=iso_datetime, help="provider run start time (timezone-aware ISO-8601)")
    parser.add_argument("--completed-at", type=iso_datetime, help="provider run completion time (timezone-aware ISO-8601)")
    parser.add_argument(
        "--execution-status",
        choices=("succeeded", "failed", "cancelled", "blocked", "unknown"),
        default="unknown",
    )
    parser.add_argument("--output", required=True, type=Path, help="JSONL destination")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing JSONL destination")
    args = parser.parse_args(argv)
    if args.commit and not SHA_RE.fullmatch(args.commit):
        parser.error("--commit must be a 7–64 character lowercase hexadecimal SHA")
    if not re.fullmatch(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", args.repository):
        parser.error("--repository must use owner/name form")
    if not re.fullmatch(r"^[A-Za-z0-9._-]{1,128}$", args.run_id):
        parser.error("--run-id must contain only letters, digits, dot, underscore, or hyphen")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.run_dir.is_dir():
        print(f"run directory does not exist: {args.run_dir}", file=sys.stderr)
        return 2
    if args.output.exists() and not args.overwrite:
        print(f"output already exists: {args.output}; pass --overwrite to replace it", file=sys.stderr)
        return 4
    events, diagnostics, valid_files, valid_personas = normalize(
        args.run_dir,
        run_id=args.run_id,
        repository=args.repository,
        commit=args.commit,
        started_at=args.started_at,
        completed_at=args.completed_at,
        execution_status=args.execution_status,
    )
    missing_personas = args.expected_personas - valid_personas
    unexpected_personas = valid_personas - args.expected_personas
    for diagnostic in diagnostics:
        print(diagnostic, file=sys.stderr)
    for persona in sorted(missing_personas):
        print(f"missing valid findings for expected persona: {persona}", file=sys.stderr)
    for persona in sorted(unexpected_personas):
        print(f"unexpected findings persona: {persona}", file=sys.stderr)
    if valid_files == 0 or missing_personas or unexpected_personas:
        print("collection incomplete: expected persona evidence is incomplete; output preserved", file=sys.stderr)
        return 3
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{args.output.name}.",
        suffix=".tmp",
        dir=args.output.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            for event in events:
                stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        Path(temp_name).replace(args.output)
    finally:
        Path(temp_name).unlink(missing_ok=True)
    print(
        f"wrote {len(events)} observed finding event(s) from {valid_files} valid findings file(s) to {args.output}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
