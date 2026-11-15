#!/usr/bin/env python3
"""Deterministic, offline SIP RFP intake after QUE admission.

This records a validated, content-hashed request envelope for a later G0 freeze. It does not run Delphi generation,
admit a DoE campaign, start a simulator, or invoke a model/provider.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

FIELD_MAP = {
    "candidate ids": "candidate_ids",
    "objective": "objective",
    "research question": "research_question",
    "comparison dimensions": "comparison_dimensions",
    "constraints and exclusions": "constraints",
    "evidence links": "evidence",
    "requested owner lane": "owner_lane",
}
SECRET_RE = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN)",
    re.I,
)


def parse_issue_form(body: str) -> dict[str, str]:
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            current = FIELD_MAP.get(heading.group(1).strip().lower())
            if current:
                fields.setdefault(current, [])
            continue
        if current:
            fields[current].append(line)
    return {
        key: "\n".join(lines).strip()
        for key, lines in fields.items()
        if "\n".join(lines).strip() not in ("", "_No response_")
    }


def _lines(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,\n]", value or "") if item.strip()]


def build_intake(body: str, issue_number: int, queue: dict[str, Any]) -> dict[str, Any]:
    if SECRET_RE.search(body):
        raise ValueError("secret-like value refused; provide public evidence references only")
    fields = parse_issue_form(body)
    required = ("objective", "research_question", "comparison_dimensions")
    missing = [name for name in required if not fields.get(name)]
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))
    candidate_ids = _lines(fields.get("candidate_ids", ""))
    if not candidate_ids:
        raise ValueError("at least one candidate ID is required")
    known = {item["id"] for item in queue.get("candidates", [])}
    unknown = sorted(set(candidate_ids) - known)
    if unknown:
        raise ValueError("unknown candidate IDs: " + ", ".join(unknown))
    evidence = _lines(fields.get("evidence", ""))
    if not evidence:
        raise ValueError("at least one evidence link or repository path is required")
    return {
        "schema_version": "sip.rfp-intake.v1",
        "intake_id": f"sip-rfp-issue-{issue_number}",
        "issue_number": issue_number,
        "candidate_queue_id": queue.get("queue_id"),
        "candidate_queue_version": queue.get("schema_version"),
        "candidate_ids": list(dict.fromkeys(candidate_ids)),
        "objective": fields["objective"],
        "research_question": fields["research_question"],
        "comparison_dimensions": _lines(fields["comparison_dimensions"]),
        "constraints": _lines(fields.get("constraints", "")),
        "evidence": evidence,
        "owner_lane": fields.get("owner_lane", "simulation-intelligence-plane"),
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "intake_state": "queued_for_g0_freeze",
        "next_gate": "freeze_brief_and_evidence_then_dispatch_existing_delphi-generate",
        "execution_authority": "QUE-admission-only",
        "external_calls": False,
        "provider_calls": False,
        "doe_admission": "not_admitted_until_design_record_and_run_evidence",
        "notes": [
            "This intake is a research request, not an adoption decision.",
            "It does not invoke Delphi generation automatically.",
            "Existing Temporal and LangGraph work must be reused rather than duplicated.",
            "Simulation outputs are not factual evidence and cannot promote graph edges."
        ]
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--body-file", required=True, type=Path)
    parser.add_argument("--queue-file", required=True, type=Path)
    parser.add_argument("--issue-number", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        body = args.body_file.read_text(encoding="utf-8")
        queue = json.loads(args.queue_file.read_text(encoding="utf-8"))
        record = build_intake(body, args.issue_number, queue)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"simulation RFP intake refused: {exc}", file=sys.stderr)
        return 2
    print(f"VALID: {record['intake_id']} candidates={len(record['candidate_ids'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
