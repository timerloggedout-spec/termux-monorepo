"""Pure, read-only coverage/provenance projection for the Historical Corpus Explorer.

This module intentionally preserves source-declared coverage and reports
reconciliation findings separately. It never treats unknown values as zero.
A warning is enough to require reconciliation; it is not permission to rewrite
or downgrade the source-declared coverage status.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_COVERAGE_STATES = {
    "COMPLETE",
    "PARTIAL_CONTINUATION_REQUIRED",
    "PARTIAL_BOUNDARY",
    "FAILED",
    "UNVERIFIED",
}


def _count(mapping: Mapping[str, Any], key: str) -> int | None:
    value = mapping.get(key)
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def project_coverage(
    manifest: Mapping[str, Any],
    build_summary: Mapping[str, Any],
    *,
    source_ref: str,
    source_sha: str,
    manifest_blob_sha: str,
) -> dict[str, Any]:
    """Build a deterministic coverage/provenance view without rewriting source facts."""
    findings: list[dict[str, str]] = []

    def finding(code: str, severity: str, message: str, field: str) -> None:
        findings.append({
            "code": code,
            "severity": severity,
            "field": field,
            "message": message,
        })

    declared_coverage = build_summary.get("coverage")
    if not isinstance(declared_coverage, str) or declared_coverage not in _COVERAGE_STATES:
        finding(
            "COVERAGE_STATUS_UNAVAILABLE",
            "warning",
            "The build summary does not declare a recognized coverage status.",
            "build_summary.coverage",
        )
        displayed_coverage = "UNVERIFIED"
    else:
        displayed_coverage = declared_coverage

    if not source_ref:
        finding("SOURCE_REF_MISSING", "error", "Source ref is unavailable.", "source_ref")
    if not _SHA_RE.fullmatch(source_sha or ""):
        finding("SOURCE_SHA_INVALID", "error", "Source SHA is missing or not a full 40-character Git SHA.", "source_sha")
    if not _SHA_RE.fullmatch(manifest_blob_sha or ""):
        finding("MANIFEST_SHA_INVALID", "error", "Manifest blob SHA is missing or invalid.", "manifest_blob_sha")

    manifest_counts = {
        "nodes": _count(manifest, "node_count"),
        "edges": _count(manifest, "edge_count"),
        "verified_edges": _count(manifest, "verified_edge_count"),
        "candidate_edges": _count(manifest, "candidate_edge_count"),
    }
    summary_counts = {
        "nodes": _count(build_summary, "node_count"),
        "edges": _count(build_summary, "edge_count"),
        "verified_edges": _count(build_summary, "verified_edge_count"),
        "candidate_edges": _count(build_summary, "candidate_edge_count"),
    }

    for key, manifest_value in manifest_counts.items():
        summary_value = summary_counts[key]
        if manifest_value is None:
            finding(
                "COUNT_UNAVAILABLE",
                "warning",
                f"The manifest does not provide a valid {key} count; it is unavailable, not zero.",
                f"manifest.{key}",
            )
        if summary_value is not None and manifest_value is not None and summary_value != manifest_value:
            finding(
                "COUNT_MISMATCH",
                "error",
                f"Manifest reports {manifest_value} {key}; build summary reports {summary_value}.",
                key,
            )

    verified = manifest_counts["verified_edges"]
    candidate = manifest_counts["candidate_edges"]
    edges = manifest_counts["edges"]
    if verified is not None and candidate is not None and edges is not None and verified + candidate != edges:
        finding(
            "EDGE_CLASSIFICATION_TOTAL_MISMATCH",
            "error",
            f"Verified ({verified}) plus candidate ({candidate}) edges does not equal total edges ({edges}).",
            "manifest.edge_count",
        )

    github_report = manifest.get("github_report")
    github_report = github_report if isinstance(github_report, Mapping) else {}
    checkpoint_eligible = github_report.get("checkpoint_eligible")
    if displayed_coverage == "COMPLETE" and checkpoint_eligible is False:
        finding(
            "COMPLETE_BUT_CHECKPOINT_INELIGIBLE",
            "warning",
            "Build summary declares COMPLETE while the GitHub report says the checkpoint is not eligible. "
            "These are separate source claims and require reconciliation; neither is silently overridden.",
            "build_summary.coverage",
        )

    history_window = manifest.get("history_window")
    if not isinstance(history_window, Mapping):
        finding(
            "HISTORY_WINDOW_UNAVAILABLE",
            "warning",
            "The manifest has no usable history-window object.",
            "manifest.history_window",
        )
        history_window = {}

    pr_count = _count(history_window, "pull_request_count")
    report_counts = github_report.get("counts")
    report_counts = report_counts if isinstance(report_counts, Mapping) else {}
    pr_stubs = _count(report_counts, "pull_request_window_stubs")
    if pr_count == 0 and pr_stubs is not None and pr_stubs > 0:
        finding(
            "PR_WINDOW_STUBS_WITH_ZERO_DECLARED_PR_COUNT",
            "warning",
            f"The history window declares zero pull requests but reports {pr_stubs} pull-request window stubs. "
            "Stubs are surfaced separately and are not counted as complete PR observations.",
            "manifest.github_report.counts.pull_request_window_stubs",
        )

    next_page = history_window.get("next_start_page")
    if next_page is not None and (
        not isinstance(next_page, int) or isinstance(next_page, bool) or next_page < 1
    ):
        finding(
            "INVALID_CONTINUATION_CURSOR",
            "error",
            "The history window continuation cursor is neither null nor a positive integer.",
            "manifest.history_window.next_start_page",
        )

    errors = sum(1 for item in findings if item["severity"] == "error")
    warnings = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "schema_version": "1.0",
        "projection": "historical_corpus_coverage",
        "provenance": {
            "source_ref": source_ref or None,
            "source_sha": source_sha if _SHA_RE.fullmatch(source_sha or "") else None,
            "manifest_blob_sha": manifest_blob_sha if _SHA_RE.fullmatch(manifest_blob_sha or "") else None,
            "generated_at": manifest.get("latest_observed_at"),
            "provenance_complete": bool(
                source_ref and _SHA_RE.fullmatch(source_sha or "")
                and _SHA_RE.fullmatch(manifest_blob_sha or "")
            ),
        },
        "coverage": {
            "status": displayed_coverage,
            "next_start_page": next_page,
            "start_page": history_window.get("start_page"),
            "checkpoint_eligible": checkpoint_eligible if isinstance(checkpoint_eligible, bool) else None,
            "checkpoint_eligibility": "ELIGIBLE" if checkpoint_eligible is True else (
                "INELIGIBLE" if checkpoint_eligible is False else "UNVERIFIED"
            ),
        },
        "counts": manifest_counts,
        "reconciliation": {
            "status": "RECONCILIATION_REQUIRED" if findings else "CONSISTENT",
            "error_count": errors,
            "warning_count": warnings,
            "findings": findings,
        },
    }
