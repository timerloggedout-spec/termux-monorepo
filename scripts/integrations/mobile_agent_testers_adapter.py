#!/usr/bin/env python3
"""Normalize locally collected Mobile Agent Testers findings into Integration Intelligence JSONL.

The collector intentionally reads only findings.json metadata. Raw reports, screenshots,
agent transcripts, and decrypted bundles remain on the trusted local machine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

INTEGRATION_ID = "mobile-agent-testers"
ADAPTER_VERSION = "1.0.0"
SEVERITIES = {"blocker", "major", "minor", "cosmetic"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\w)\+?\d[\d(). -]{7,}\d(?!\w)")
TOKEN_RE = re.compile(
    r"\b(?:bearer|token|api[_ -]?key|secret)\s*[:=]?\s*[A-Za-z0-9._~+/=-]{8,}",
    re.I,
)
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
PERSONA_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
SHA_RE = re.compile(r"^[0-9a-f]{7,64}$")


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
    # Mirrors the provider's own collector layout: <persona>/results/findings.json.
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
) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    diagnostics: list[str] = []
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
        source_digest = digest_file(path)
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
            events.append(event)
    return events, diagnostics


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path, help="trusted, locally decrypted run directory")
    parser.add_argument("--run-id", required=True, help="immutable provider workflow run ID")
    parser.add_argument("--repository", default="timerloggedout-spec/termux-monorepo")
    parser.add_argument("--commit", help="tested source commit SHA")
    parser.add_argument("--started-at", help="provider run start time (ISO-8601)")
    parser.add_argument("--completed-at", help="provider run completion time (ISO-8601)")
    parser.add_argument(
        "--execution-status",
        choices=("succeeded", "failed", "cancelled", "blocked", "unknown"),
        default="unknown",
    )
    parser.add_argument("--output", required=True, type=Path, help="JSONL destination")
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
    events, diagnostics = normalize(
        args.run_dir,
        run_id=args.run_id,
        repository=args.repository,
        commit=args.commit,
        started_at=args.started_at,
        completed_at=args.completed_at,
        execution_status=args.execution_status,
    )
    for diagnostic in diagnostics:
        print(diagnostic, file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for event in events:
            stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"wrote {len(events)} observed finding event(s) to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
