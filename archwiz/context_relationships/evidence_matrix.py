"""Project bounded, metadata-only relationship evidence from an audit artifact.

This is intentionally a read-only decision-support projection.  It does not
publish a canonical graph, infer causality, rank providers, or authorize writes.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from archwiz.context_relationships.compiler import CompilationError, reject_sensitive_values

MATRIX_SCHEMA = "context-relationship-evidence-matrix/v1"
AUDIT_SCHEMA = "context-relationship-index/v1"


class EvidenceMatrixError(ValueError):
    """An audit record cannot safely be projected as relationship evidence."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_id(prefix: str, value: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}:{digest}"


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvidenceMatrixError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise EvidenceMatrixError(f"{label} must be an array")
    return value


def optional_text(value: Any, label: str) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise EvidenceMatrixError(f"{label} must be a string when present")
    return value


def require_timestamp(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise EvidenceMatrixError(f"{label} must be a non-empty ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceMatrixError(f"{label} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise EvidenceMatrixError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def reject_unsafe(value: Any, label: str) -> None:
    try:
        reject_sensitive_values(value, label, ())
    except CompilationError as exc:
        raise EvidenceMatrixError(str(exc)) from exc


def github_locator(repository: str, path: str) -> str:
    return f"github-api://repos/{repository}/{path.lstrip('/')}"


def exact_roots(correlation: Mapping[str, Any]) -> list[str]:
    roots: list[str] = []
    for key, prefix in (("pr_number", "pr"), ("issue_number", "issue")):
        number = correlation.get(key)
        if isinstance(number, int) and number > 0:
            roots.append(f"{prefix}:{number}")
    return roots


def graph_coverage(summary: Mapping[str, Any] | None, source_sha: str | None) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if summary is None:
        return (
            {"state": "not_loaded", "reason": "canonical graph summary was not supplied"},
            [{"subject": "canonical_graph", "reason": "canonical graph summary was not supplied"}],
        )
    reject_unsafe(summary, "graph_summary")
    history = summary.get("history_window")
    history = require_mapping(history, "graph_summary.history_window") if history is not None else {}
    gaps: list[dict[str, str]] = []
    ref = optional_text(summary.get("ref"), "graph_summary.ref")
    parser_failures = summary.get("parser_failures", 0)
    if not isinstance(parser_failures, int) or isinstance(parser_failures, bool) or parser_failures < 0:
        raise EvidenceMatrixError("graph_summary.parser_failures must be a non-negative integer")
    if ref != "master":
        gaps.append({"subject": "canonical_graph", "reason": "published graph ref is not master"})
    if history.get("issues_complete") is False or history.get("pull_requests_complete") is False:
        gaps.append({"subject": "canonical_graph", "reason": "historical GitHub coverage is incomplete"})
    if parser_failures:
        gaps.append({"subject": "canonical_graph", "reason": "parser failures are disclosed by the graph summary"})
    if source_sha:
        gaps.append({
            "subject": "canonical_graph",
            "reason": "summary has no SHA binding that can attest the audit source revision",
        })
    state = "covered" if not gaps else "partial"
    coverage = {
        "state": state,
        "ref": ref,
        "history_window": {
            "issues_complete": history.get("issues_complete"),
            "pull_requests_complete": history.get("pull_requests_complete"),
            "next_start_page": history.get("next_start_page"),
        },
        "parser_failures": parser_failures,
    }
    return coverage, gaps


def relationship_record(
    *,
    relationship_type: str,
    direction: str,
    classification: str,
    disposition: str,
    risk_state: str,
    risk_reasons: list[str],
    locator: str,
    authority: str,
    provenance: str,
    observed_at: str,
    scope: Mapping[str, Any],
    binding: Mapping[str, Any],
    details: Mapping[str, Any],
    outcome: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "relationship_type": relationship_type,
        "direction": direction,
        "classification": classification,
        "locator": locator,
        "binding": dict(binding),
        "details": dict(details),
    }
    record = {
        "id": stable_id("evidence", payload),
        "exact_scope": dict(scope),
        "relationship": {"type": relationship_type, "direction": direction},
        "classification": classification,
        "disposition": disposition,
        "risk": {"state": risk_state, "reasons": sorted(set(risk_reasons))},
        "evidence": {
            "authority": authority,
            "provenance": provenance,
            "immutable_locator": locator,
            "observed_at": observed_at,
        },
        "binding": dict(binding),
        "freshness": {"state": "observed", "observed_at": observed_at},
        "details": dict(details),
    }
    if outcome is not None:
        record["outcome"] = dict(outcome)
    return record


def project_evidence_matrix(
    audit: Mapping[str, Any], graph_summary: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Return a deterministic, safety-checked matrix from one audit artifact.

    The audit is the source of event and check metadata.  The optional graph
    summary only describes coverage/freshness; it never causes a relationship to
    be asserted and cannot be treated as current lineage authority.
    """
    audit = require_mapping(audit, "audit")
    reject_unsafe(audit, "audit")
    if audit.get("schema") != AUDIT_SCHEMA:
        raise EvidenceMatrixError(f"audit.schema must be {AUDIT_SCHEMA!r}")
    observed_at = require_timestamp(audit.get("observed_at"), "audit.observed_at")
    repository = optional_text(audit.get("repository"), "audit.repository") or "unknown"
    source_sha = optional_text(audit.get("source_sha"), "audit.source_sha")
    correlation = require_mapping(audit.get("correlation", {}), "audit.correlation")
    scope = {
        "repository": repository,
        "roots": exact_roots(correlation),
        "fuzzy_fallback": False,
    }
    binding = {
        "source_sha": source_sha,
        "workflow_run_id": optional_text(audit.get("workflow_run_id"), "audit.workflow_run_id"),
        "workflow_run_attempt": optional_text(audit.get("workflow_run_attempt"), "audit.workflow_run_attempt"),
        "event_name": optional_text(audit.get("event_name"), "audit.event_name"),
    }
    lead_events = [require_mapping(item, "audit.lead_events item") for item in require_list(audit.get("lead_events"), "audit.lead_events")]
    lag_events = [require_mapping(item, "audit.lag_events item") for item in require_list(audit.get("lag_events"), "audit.lag_events")]
    records: list[dict[str, Any]] = []
    gaps: list[dict[str, str]] = []

    audit_bound = bool(binding["workflow_run_id"] and source_sha)
    audit_locator = github_locator(repository, f"actions/runs/{binding['workflow_run_id']}") if binding["workflow_run_id"] else github_locator(repository, "actions")
    records.append(relationship_record(
        relationship_type="AUDITS_CONTEXT",
        direction="inbound",
        classification="verified" if audit_bound else "candidate",
        disposition="accepted" if audit_bound else "quarantined",
        risk_state="none" if audit_bound else "missing_binding",
        risk_reasons=[] if audit_bound else ["audit lacks a complete workflow-run and source-SHA binding"],
        locator=audit_locator,
        authority="github_actions_read_only" if audit_bound else "local_read_only_probe",
        provenance="context_relationship_audit" if audit_bound else "local_read_only_probe",
        observed_at=observed_at,
        scope=scope,
        binding=binding,
        details={"event_name": binding["event_name"]},
    ))

    for event in lead_events:
        kind = optional_text(event.get("kind"), "lead_event.kind") or "unknown"
        if kind == "comment":
            comment_id = event.get("id")
            if not isinstance(comment_id, int) or isinstance(comment_id, bool) or comment_id < 1:
                gaps.append({"subject": "comment", "reason": "comment metadata lacks an immutable comment identifier"})
                continue
            number = correlation.get("pr_number") or correlation.get("issue_number")
            issue_path = f"issues/{number}#issuecomment-{comment_id}" if isinstance(number, int) else f"issues/comments/{comment_id}"
            records.append(relationship_record(
                relationship_type="COMMENTS_ON_CONTEXT",
                direction="inbound",
                classification="verified",
                disposition="accepted",
                risk_state="none",
                risk_reasons=[],
                locator=github_locator(repository, issue_path),
                authority="github_api_read",
                provenance="issue_comment_metadata",
                observed_at=optional_text(event.get("created_at"), "lead_event.created_at") or observed_at,
                scope=scope,
                binding=binding,
                details={"comment_id": comment_id, "author": optional_text(event.get("author"), "lead_event.author")},
            ))
        elif kind.endswith("_warning"):
            gaps.append({"subject": kind, "reason": "collector query returned a warning; no relationship was asserted"})

    for event in lag_events:
        kind = optional_text(event.get("kind"), "lag_event.kind") or "unknown"
        if kind == "check":
            check_id = event.get("run_id")
            completed_at = optional_text(event.get("completed_at"), "check.completed_at")
            started_at = optional_text(event.get("started_at"), "check.started_at")
            independently_verified = isinstance(check_id, int) and check_id > 0 and bool(source_sha) and bool(completed_at)
            records.append(relationship_record(
                relationship_type="CHECKS_CONTEXT",
                direction="outbound",
                classification="verified" if independently_verified else "candidate",
                disposition="accepted" if independently_verified else "quarantined",
                risk_state="none" if independently_verified else "missing_binding",
                risk_reasons=[] if independently_verified else ["check lacks an independently bound completed source-SHA outcome"],
                locator=github_locator(repository, f"check-runs/{check_id}") if isinstance(check_id, int) and check_id > 0 else github_locator(repository, f"commits/{source_sha or 'unknown'}/check-runs"),
                authority="github_checks_api",
                provenance="check_run_metadata",
                observed_at=completed_at or started_at or observed_at,
                scope=scope,
                binding={**binding, "check_run_id": check_id},
                details={
                    "name": optional_text(event.get("name"), "check.name"),
                    "status": optional_text(event.get("status"), "check.status"),
                    "conclusion": optional_text(event.get("conclusion"), "check.conclusion"),
                },
                outcome={
                    "independently_verified": independently_verified,
                    "binding": {"source_sha": source_sha, "check_run_id": check_id, "completed_at": completed_at},
                },
            ))
        elif kind.endswith("_warning"):
            gaps.append({"subject": kind, "reason": "collector query returned WARNING/UNKNOWN; no successful outcome linkage was asserted"})

    counts = Counter(record["evidence"]["immutable_locator"] for record in records)
    duplicate_concentration = [
        {"immutable_locator": locator, "count": count, "classification": "duplicate"}
        for locator, count in sorted(counts.items())
        if count > 1
    ]
    for record in records:
        count = counts[record["evidence"]["immutable_locator"]]
        record["duplicate_concentration"] = {"count": count, "classification": "duplicate" if count > 1 else "unique"}

    coverage, graph_gaps = graph_coverage(graph_summary, source_sha)
    gaps.extend(graph_gaps)
    verified = [record for record in records if record["classification"] == "verified"]
    candidate = [record for record in records if record["classification"] == "candidate"]
    result = {
        "schema": MATRIX_SCHEMA,
        "decision_support_only": True,
        "observed_at": observed_at,
        "scope": scope,
        "source_audit": {"schema": AUDIT_SCHEMA, **binding},
        "records": sorted(records, key=lambda item: item["id"]),
        "verified_records": [record["id"] for record in sorted(verified, key=lambda item: item["id"])],
        "candidate_records": [record["id"] for record in sorted(candidate, key=lambda item: item["id"])],
        "authority_distribution": dict(sorted(Counter(record["evidence"]["authority"] for record in records).items())),
        "provenance_distribution": dict(sorted(Counter(record["evidence"]["provenance"] for record in records).items())),
        "duplicate_concentration": duplicate_concentration,
        "coverage": {
            "expected": ["audit_event_metadata", "check_run_metadata", "canonical_graph_summary"],
            "graph": coverage,
            "gaps": sorted(gaps, key=canonical_json),
        },
        "limitations": [
            "The matrix is decision-support only and does not authorize provider, routing, or write effects.",
            "Temporal correlation is not causal attribution.",
            "Typed roots are exact; no fuzzy fallback is used.",
            "Raw issue, comment, and review bodies are rejected and never persisted.",
        ],
    }
    reject_unsafe(result, "matrix")
    return result
