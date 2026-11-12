#!/usr/bin/env python3
"""Audit merged branches and evaluate production deployment cooldowns and timing quotas."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any


def _parse_iso8601(timestamp_str: str | None) -> datetime | None:
    if not timestamp_str:
        return None
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def audit_merged_prs(pr_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Audit merged pull requests for unreviewed implementations or missing dismissal justifications."""
    violations: list[dict[str, Any]] = []

    for pr in pr_data:
        pr_number = pr.get("number")
        pr_title = pr.get("title", "")
        pr_author = pr.get("author", "")
        is_merged = pr.get("merged", False) or pr.get("state") == "MERGED"
        reviews = pr.get("reviews") or []

        if not is_merged:
            continue

        skipped_reviews_unjustified = []
        has_approvals = False

        for review in reviews:
            state = review.get("state")
            if state == "APPROVED":
                has_approvals = True
            elif state == "DISMISSED":
                justification = str(
                    review.get("dismissal_justification")
                    or review.get("justification")
                    or ""
                ).strip()
                if not justification:
                    reviewer = (review.get("user") or {}).get("login", "unknown")
                    skipped_reviews_unjustified.append(reviewer)

        if skipped_reviews_unjustified or not has_approvals:
            violations.append({
                "pr_number": pr_number,
                "title": pr_title,
                "author": pr_author,
                "has_approvals": has_approvals,
                "unjustified_dismissed_reviews": skipped_reviews_unjustified,
                "reason": (
                    "Dismissed review missing justification"
                    if skipped_reviews_unjustified
                    else "Merged without required approvals"
                ),
            })

    return violations


def evaluate_cooldown_and_quotas(
    events: list[dict[str, Any]], cooldown_seconds: int = 300
) -> dict[str, Any]:
    """Verify timing quotas and minimum cooldown intervals between deployments or PR merges."""
    cooldown_violations: list[dict[str, Any]] = []
    parsed_events = []

    for event in events:
        ts = _parse_iso8601(event.get("timestamp"))
        if ts:
            parsed_events.append((ts, event))

    parsed_events.sort(key=lambda x: x[0])

    for i in range(1, len(parsed_events)):
        prev_time, prev_event = parsed_events[i - 1]
        curr_time, curr_event = parsed_events[i]
        delta_seconds = (curr_time - prev_time).total_seconds()

        if delta_seconds < cooldown_seconds:
            cooldown_violations.append({
                "prev_event_id": prev_event.get("id"),
                "curr_event_id": curr_event.get("id"),
                "elapsed_seconds": delta_seconds,
                "required_cooldown_seconds": cooldown_seconds,
                "reason": f"Deployment frequency violated cooldown ({delta_seconds:.1f}s < {cooldown_seconds}s)",
            })

    return {
        "schema": "termux.merged-branch-audit/v1",
        "total_events": len(events),
        "cooldown_violations": cooldown_violations,
        "status": "PASS" if not cooldown_violations else "WARNING",
    }


def generate_bug_issue_payload(audit_findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate structured issue payload tagged for skipped review or unreviewed PR implementations."""
    body_lines = [
        "## Audit Warning: Merged PRs with Skipped/Unjustified Reviews",
        "",
        "The following merged pull requests failed governance verification:",
        "",
    ]

    for finding in audit_findings:
        pr_num = finding.get("pr_number", "N/A")
        title = finding.get("title", "Untitled")
        author = finding.get("author", "unknown")
        reason = finding.get("reason", "Skipped review audit violation")
        body_lines.append(f"- **PR #{pr_num}**: `{title}` (Author: @{author}) - {reason}")

    body_lines.extend([
        "",
        "### Action Required",
        "Please review the PR implementations listed above and attach appropriate justification or post-hoc safety review comments.",
    ])

    return {
        "title": f"Governance Audit: {len(audit_findings)} merged PR(s) skipped required review justification",
        "body": "\n".join(body_lines),
        "labels": ["bug", "skipped-review-audit", "governance"],
    }


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError) as exc:
        print(
            json.dumps({
                "schema": "termux.merged-branch-audit/v1",
                "error": f"Invalid JSON input: {exc}",
            })
        )
        return 2

    pr_findings = audit_merged_prs(data.get("pull_requests", []))
    cooldown_report = evaluate_cooldown_and_quotas(
        data.get("events", []),
        cooldown_seconds=data.get("cooldown_seconds", 300),
    )

    issue_payload = generate_bug_issue_payload(pr_findings) if pr_findings else None

    result = {
        "schema": "termux.merged-branch-audit/v1",
        "pr_audit_findings": pr_findings,
        "cooldown_report": cooldown_report,
        "issue_payload": issue_payload,
    }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
