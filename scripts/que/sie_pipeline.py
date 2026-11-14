#!/usr/bin/env python3
"""Deterministic QUE SIE lifecycle contract and transition validator.

DO: validate stage progression and source identity before adapters perform effects.
PDDL is modeled as a Siglary formal-planning subdomain; this module owns no planner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any

STAGES = (
    "OBSERVE", "TRIAGE", "RESEARCH", "RFP", "DELPHI",
    "DESIGN", "CLAIM", "IMPLEMENT", "VERIFY", "PROMOTE", "LEARN",
)
STATES = {"PENDING", "READY", "ACTIVE", "COMPLETED", "BLOCKED", "REJECTED", "SUPERSEDED"}
SOURCE_KINDS = {
    "workflow_run", "queue_item", "stall_gap", "feed_freshness",
    "desk_filing", "research_opportunity",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
TERMINAL = {"REJECTED", "SUPERSEDED"}
BLOCKING = {"BLOCKED"}


class StageValidationError(ValueError):
    """Raised when a stage receipt or transition violates the contract."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def stable_event_id(source_kind: str, source_id: str, source_revision: str) -> str:
    """Return a stable idempotency key for one source event revision."""
    if source_kind not in SOURCE_KINDS:
        raise StageValidationError(f"unsupported source kind: {source_kind}")
    for name, value in (("source_id", source_id), ("source_revision", source_revision)):
        if not isinstance(value, str) or not value.strip():
            raise StageValidationError(f"{name} must be a non-empty string")
    payload = {"source_kind": source_kind, "source_id": source_id, "source_revision": source_revision}
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def item_key(source_kind: str, source_id: str, failure_class: str) -> str:
    """Group repeated observations of the same logical work item."""
    if source_kind not in SOURCE_KINDS:
        raise StageValidationError(f"unsupported source kind: {source_kind}")
    for name, value in (("source_id", source_id), ("failure_class", failure_class)):
        if not isinstance(value, str) or not value.strip():
            raise StageValidationError(f"{name} must be a non-empty string")
    payload = {"source_kind": source_kind, "source_id": source_id, "failure_class": failure_class}
    return hashlib.sha256(canonical_json(payload)).hexdigest()[:24]


def validate_receipt(receipt: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(receipt, dict):
        return ["receipt: expected object"]
    required = ("schema", "event_id", "item_key", "stage", "state", "source",
                "observed_at", "repository", "ref", "sha", "evidence_refs")
    for field in required:
        if field not in receipt:
            errors.append(f"missing field: {field}")
    if receipt.get("schema") != "que.sie-stage/v1":
        errors.append("schema: expected que.sie-stage/v1")
    for field in ("event_id", "item_key", "ref"):
        if not isinstance(receipt.get(field), str) or not receipt[field].strip():
            errors.append(f"{field}: expected non-empty string")
    if isinstance(receipt.get("event_id"), str) and not re.fullmatch(r"[0-9a-f]{64}", receipt["event_id"]):
        errors.append("event_id: expected SHA-256 identity")
    if isinstance(receipt.get("item_key"), str) and not re.fullmatch(r"[0-9a-f]{24}", receipt["item_key"]):
        errors.append("item_key: expected 24-character stable identity")
    if receipt.get("stage") not in STAGES:
        errors.append("stage: unsupported lifecycle stage")
    if receipt.get("state") not in STATES:
        errors.append("state: unsupported lifecycle state")
    source = receipt.get("source")
    if not isinstance(source, dict):
        errors.append("source: expected object")
    else:
        if source.get("kind") not in SOURCE_KINDS:
            errors.append("source.kind: unsupported source kind")
        if not isinstance(source.get("id"), str) or not source["id"].strip():
            errors.append("source.id: expected non-empty string")
        if source.get("url") is not None and not isinstance(source.get("url"), str):
            errors.append("source.url: expected string or null")
    repo = receipt.get("repository")
    if not isinstance(repo, str) or not re.fullmatch(r"[^/]+/[^/]+", repo):
        errors.append("repository: expected owner/repository")
    sha = receipt.get("sha")
    if sha is not None and (not isinstance(sha, str) or not SHA_RE.fullmatch(sha)):
        errors.append("sha: expected lowercase Git SHA or null")
    observed = receipt.get("observed_at")
    if not isinstance(observed, str):
        errors.append("observed_at: expected ISO timestamp")
    else:
        try:
            parsed = datetime.fromisoformat(observed.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append("observed_at: timezone offset required")
        except ValueError:
            errors.append("observed_at: invalid ISO timestamp")
    refs = receipt.get("evidence_refs")
    if not isinstance(refs, list) or not all(isinstance(x, str) and x.strip() for x in refs):
        errors.append("evidence_refs: expected array of non-empty strings")
    for field in ("owner_role", "claim_class", "reason"):
        if receipt.get(field) is not None and not isinstance(receipt.get(field), str):
            errors.append(f"{field}: expected string or null")
    digest = receipt.get("package_digest")
    if digest is not None and (not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest)):
        errors.append("package_digest: expected SHA-256 digest or null")
    return errors


def next_stage(stage: str) -> str | None:
    if stage not in STAGES:
        raise StageValidationError(f"unknown stage: {stage}")
    index = STAGES.index(stage)
    return STAGES[index + 1] if index + 1 < len(STAGES) else None


def validate_transition(previous: dict, current: dict) -> list[str]:
    """Validate a single forward transition; terminal states require a new lineage."""
    errors = validate_receipt(previous) + validate_receipt(current)
    if errors:
        return [f"previous: {e}" for e in validate_receipt(previous)] + [f"current: {e}" for e in validate_receipt(current)]
    if previous["item_key"] != current["item_key"]:
        errors.append("item_key: transition must preserve logical work identity")
    if previous["source"] != current["source"]:
        errors.append("source: transition must preserve source identity")
    if previous["state"] in TERMINAL:
        errors.append("state: terminal lineage requires a new item")
    if previous["state"] == "BLOCKED" and current["stage"] != previous["stage"]:
        errors.append("stage: blocked item resumes at the same stage")
    if current["stage"] != next_stage(previous["stage"]) and not (
        previous["state"] == "BLOCKED" and current["stage"] == previous["stage"]
    ):
        errors.append("stage: transition must advance exactly one stage")
    if previous["state"] != "COMPLETED" and previous["state"] != "BLOCKED":
        errors.append("state: previous stage must be COMPLETED or BLOCKED")
    if previous["state"] == "BLOCKED" and current["state"] not in {"READY", "ACTIVE", "BLOCKED"}:
        errors.append("state: blocked stage resumes as READY, ACTIVE or BLOCKED")
    return errors


def build_receipt(*, source_kind: str, source_id: str, source_revision: str,
                  failure_class: str, stage: str = "OBSERVE", state: str = "COMPLETED",
                  repository: str = "timerloggedout-spec/termux-monorepo",
                  ref: str = "master", sha: str | None = None,
                  observed_at: str | None = None, evidence_refs: list[str] | None = None,
                  owner_role: str | None = None, claim_class: str | None = None,
                  package_digest: str | None = None, reason: str | None = None) -> dict:
    at = observed_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    receipt = {
        "schema": "que.sie-stage/v1",
        "event_id": stable_event_id(source_kind, source_id, source_revision),
        "item_key": item_key(source_kind, source_id, failure_class),
        "stage": stage,
        "state": state,
        "source": {"kind": source_kind, "id": source_id, "url": None},
        "observed_at": at,
        "repository": repository,
        "ref": ref,
        "sha": sha,
        "owner_role": owner_role,
        "claim_class": claim_class,
        "evidence_refs": sorted(set(evidence_refs or [])),
        "package_digest": package_digest,
        "reason": reason,
    }
    errors = validate_receipt(receipt)
    if errors:
        raise StageValidationError("; ".join(errors))
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="validate deterministic contract primitives")
    args = parser.parse_args(argv)
    if args.self_test:
        first = stable_event_id("workflow_run", "123", "a" * 40)
        second = stable_event_id("workflow_run", "123", "a" * 40)
        if first != second:
            print("SIE contract self-test failed: event identity drift")
            return 1
        receipt = build_receipt(source_kind="workflow_run", source_id="123",
                                source_revision="a" * 40, failure_class="ci",
                                sha="a" * 40, observed_at="2026-11-13T00:00:00Z")
        if validate_receipt(receipt):
            print("SIE contract self-test failed: invalid generated receipt")
            return 1
        print("SIE contract self-test passed.")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
