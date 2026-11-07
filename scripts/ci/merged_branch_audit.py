#!/usr/bin/env python3
"""Audit merged branches for unreviewed implementations, missing dismissal justifications, timing quotas, and cooldowns."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Sequence


def _parse_iso8601(val: str | int | float | None) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val, tz=timezone.utc)
    if not isinstance(val, str):
        return None
    val_str = val.strip()
    if not val_str:
        return None
    try:
        if val_str.endswith("Z"):
            val_str = val_str[:-1] + "+00:00"
        return datetime.fromisoformat(val_str)
    except ValueError:
        return None


def audit_merged_prs(merged_prs: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Audit merged PRs for unreviewed implementations or missing dismissal justifications."""
    findings: list[dict[str, Any]] = []

    for pr in merged_prs:
        pr_number = pr.get("number")
        pr_title = str(pr.get("title") or "")
        html_url = str(pr.get("html_url") or "")
        author = str(pr.get("author") or (pr.get("user") or {}).get("login") or "").lower()
        merged_at = str(pr.get("merged_at") or "")
        reviews = pr.get("reviews") or []

        # Audit dismissed reviews for missing justification
        for review in reviews:
            state = str(review.get("state") or "").upper()
            if state == "DISMISSED":
                justification = str(
                    review.get("dismissal_justification") or review.get("justification") or ""
                ).strip()
                if not justification:
                    findings.append({
                        "pr_number": pr_number,
                        "pr_title": pr_title,
                        "html_url": html_url,
                        "author": author,
                        "merged_at": merged_at,
                        "violation_type": "missing_dismissal_justification",
                        "reason": f"PR #{pr_number} has a dismissed review with no dismissal justification",
                    })
                    break

        # Check for human approving reviews
        valid_approvals = 0
        latest_by_reviewer: dict[str, dict[str, Any]] = {}

        for review in reviews:
            user = review.get("user") or {}
            login = str(user.get("login") or "").lower()
            user_type = str(user.get("type") or "")

            if not login or user_type == "Bot" or login == author:
                continue

            state = str(review.get("state") or "").upper()
            if state in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED"):
                latest_by_reviewer[login] = review

        for login, review in latest_by_reviewer.items():
            if str(review.get("state") or "").upper() == "APPROVED":
                valid_approvals += 1

        if valid_approvals == 0:
            findings.append({
                "pr_number": pr_number,
                "pr_title": pr_title,
                "html_url": html_url,
                "author": author,
                "merged_at": merged_at,
                "violation_type": "unreviewed_implementation",
                "reason": f"PR #{pr_number} was merged without any human approving reviews",
            })

    return findings


def evaluate_cooldown_and_quotas(
    events: Sequence[dict[str, Any]],
    min_cooldown_seconds: int = 300,
    quota_limit: int = 10,
    window_seconds: int = 3600,
) -> dict[str, Any]:
    """Verify timing quotas and minimum cooldown intervals between merge events and deployments."""
    parsed_events: list[tuple[datetime, dict[str, Any]]] = []
    for ev in events:
        ts = _parse_iso8601(ev.get("timestamp") or ev.get("time") or ev.get("created_at"))
        if ts is not None:
            parsed_events.append((ts, ev))

    parsed_events.sort(key=lambda x: x[0])

    violations: list[dict[str, Any]] = []
    reasons: list[str] = []

    # Quota check (sliding window)
    for i, (ts, ev) in enumerate(parsed_events):
        window_start = ts.timestamp() - window_seconds
        count = sum(1 for t, _ in parsed_events if window_start <= t.timestamp() <= ts.timestamp())
        if count > quota_limit:
            reason = f"Event at {ts.isoformat()} exceeded quota limit of {quota_limit} events per {window_seconds}s (found {count})"
            if reason not in reasons:
                reasons.append(reason)
            violations.append({
                "violation_type": "quota_exceeded",
                "timestamp": ts.isoformat(),
                "event": ev,
                "count": count,
                "quota_limit": quota_limit,
                "window_seconds": window_seconds,
            })

    # Cooldown check
    for i in range(1, len(parsed_events)):
        prev_ts, prev_ev = parsed_events[i - 1]
        curr_ts, curr_ev = parsed_events[i]
        delta_sec = (curr_ts - prev_ts).total_seconds()
        if delta_sec < min_cooldown_seconds:
            reason = (
                f"Cooldown violation between event at {prev_ts.isoformat()} and {curr_ts.isoformat()}: "
                f"{delta_sec:.1f}s < required {min_cooldown_seconds}s"
            )
            if reason not in reasons:
                reasons.append(reason)
            violations.append({
                "violation_type": "cooldown_violation",
                "prev_timestamp": prev_ts.isoformat(),
                "curr_timestamp": curr_ts.isoformat(),
                "delta_seconds": delta_sec,
                "min_cooldown_seconds": min_cooldown_seconds,
                "prev_event": prev_ev,
                "curr_event": curr_ev,
            })

    admit = "admit" if not violations else "deny"

    return {
        "admit": admit,
        "reasons": reasons,
        "violations": violations,
        "event_count": len(parsed_events),
    }


def generate_bug_issue_payload(audit_finding: dict[str, Any]) -> dict[str, Any]:
    """Format structured GitHub issue payloads tagged with bug, skipped-review-audit, and governance."""
    pr_num = audit_finding.get("pr_number")
    pr_title = audit_finding.get("pr_title") or f"PR #{pr_num}"
    html_url = audit_finding.get("html_url") or ""
    author = audit_finding.get("author") or "unknown"
    merged_at = audit_finding.get("merged_at") or "unknown"
    violation_type = audit_finding.get("violation_type") or "unreviewed_implementation"
    reason = audit_finding.get("reason") or "Skipped review or missing dismissal justification detected."

    issue_title = f"Audit Violation: {violation_type.replace('_', ' ').title()} on PR #{pr_num}"

    body_lines = [
        "## Governance & Review Audit Finding",
        "",
        f"**PR Number:** #{pr_num}",
        f"**PR Title:** {pr_title}",
        f"**PR URL:** {html_url}",
        f"**Author:** @{author}",
        f"**Merged At:** {merged_at}",
        f"**Violation Type:** `{violation_type}`",
        "",
        "### Detail",
        f"{reason}",
        "",
        "---",
        "*(Automated finding generated by `scripts/ci/merged_branch_audit.py`)*",
    ]

    return {
        "title": issue_title,
        "body": "\n".join(body_lines),
        "labels": ["bug", "skipped-review-audit", "governance"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Merged Branch Audit & Timing Quota Evaluator")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    parser.add_argument("--input", type=str, help="Path to input JSON snapshot")

    args = parser.parse_args()

    snapshot: dict[str, Any] = {}
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            snapshot = json.load(f)
    elif not sys.stdin.isatty():
        try:
            snapshot = json.load(sys.stdin)
        except (json.JSONDecodeError, TypeError):
            snapshot = {}

    merged_prs = snapshot.get("merged_prs") or []
    events = snapshot.get("events") or []

    findings = audit_merged_prs(merged_prs)
    quota_res = evaluate_cooldown_and_quotas(events)

    issues = [generate_bug_issue_payload(f) for f in findings]

    report = {
        "schema": "termux.merged-branch-audit/v1",
        "audit_findings": findings,
        "quota_evaluation": quota_res,
        "generated_issues": issues,
    }

    print(json.dumps(report, indent=2))

    return 1 if (findings or quota_res["admit"] == "deny") else 0


if __name__ == "__main__":
    raise SystemExit(main())
