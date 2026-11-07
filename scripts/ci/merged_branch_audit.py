#!/usr/bin/env python3
"""Audit merged pull requests, timing quotas, cooldowns, and generate governance bug issue payloads."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def audit_merged_prs(merged_prs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Audit merged pull requests for unreviewed implementations or missing dismissal justifications."""
    findings_list: list[dict[str, Any]] = []

    for pr in merged_prs:
        pr_number = pr.get("number") or pr.get("pr_number")
        title = pr.get("title", "")
        author = pr.get("author") or (pr.get("user") or {}).get("login", "")
        url = pr.get("url") or pr.get("html_url", "")
        reviews = pr.get("reviews") or []
        head_sha = pr.get("head_sha") or pr.get("head", {}).get("sha", "")

        reasons: list[str] = []

        # 1. Check for human approvals on current or valid commits
        human_approvals = 0
        latest_by_reviewer: dict[str, dict[str, Any]] = {}

        for review in reviews:
            user = review.get("user") or {}
            login = str(user.get("login") or review.get("reviewer") or "").lower()
            if not login or user.get("type") == "Bot" or login == str(author).lower():
                continue

            commit_id = review.get("commit_id") or review.get("commit_sha")
            if head_sha and commit_id and commit_id != head_sha:
                continue

            state = review.get("state")
            if state == "PENDING" or not review.get("submitted_at"):
                continue

            submitted_at = _parse_time(review.get("submitted_at"))
            prior = latest_by_reviewer.get(login)
            prior_time = _parse_time(prior.get("submitted_at")) if prior else None

            if prior is None or (submitted_at and prior_time and submitted_at >= prior_time):
                latest_by_reviewer[login] = review

        for login, review in latest_by_reviewer.items():
            if review.get("state") == "APPROVED":
                human_approvals += 1

        if human_approvals == 0:
            reasons.append("unreviewed_implementation")

        # 2. Check for missing dismissal justification
        for review in reviews:
            if review.get("state") == "DISMISSED":
                justification = str(
                    review.get("dismissal_justification")
                    or review.get("justification")
                    or ""
                ).strip()
                if not justification:
                    reasons.append("missing_dismissal_justification")
                    break

        # 3. Check for missed review implementations / unaddressed changes requested
        if any(r.get("state") == "CHANGES_REQUESTED" for r in latest_by_reviewer.values()):
            reasons.append("missed_review_implementation")

        if reasons:
            findings_list.append({
                "pr_number": pr_number,
                "title": title,
                "author": author,
                "url": url,
                "findings": reasons,
                "severity": "high" if "unreviewed_implementation" in reasons else "medium",
            })

    return findings_list


def evaluate_cooldown_and_quotas(
    merged_prs: list[dict[str, Any]],
    deployments: list[dict[str, Any]],
    min_cooldown_seconds: int = 300,
    max_deployments_per_hour: int = 5,
) -> dict[str, Any]:
    """Verify timing quotas and minimum cooldown intervals between PR merge events and deployments."""
    cooldown_violations: list[dict[str, Any]] = []
    quota_violations: list[dict[str, Any]] = []

    # Sort events by timestamp
    parsed_merges = []
    for pr in merged_prs:
        merged_at_str = pr.get("merged_at") or pr.get("merged_time")
        dt = _parse_time(merged_at_str)
        if dt:
            parsed_merges.append({
                "pr_number": pr.get("number") or pr.get("pr_number"),
                "merged_at": dt,
            })

    parsed_deployments = []
    for dep in deployments:
        dep_at_str = dep.get("created_at") or dep.get("timestamp") or dep.get("deployed_at")
        dt = _parse_time(dep_at_str)
        if dt:
            parsed_deployments.append({
                "deployment_id": dep.get("id") or dep.get("deployment_id"),
                "environment": dep.get("environment", "production"),
                "timestamp": dt,
            })

    parsed_deployments.sort(key=lambda d: d["timestamp"])

    # Check minimum cooldown after merge
    for dep in parsed_deployments:
        dep_time = dep["timestamp"]
        for merge in parsed_merges:
            merge_time = merge["merged_at"]
            if merge_time <= dep_time:
                delta_seconds = (dep_time - merge_time).total_seconds()
                if 0 <= delta_seconds < min_cooldown_seconds:
                    cooldown_violations.append({
                        "deployment_id": dep["deployment_id"],
                        "pr_number": merge["pr_number"],
                        "delta_seconds": delta_seconds,
                        "min_required_seconds": min_cooldown_seconds,
                        "message": (
                            f"Deployment {dep['deployment_id']} occurred {delta_seconds:.0f}s "
                            f"after PR #{merge['pr_number']} merge (min cooldown: {min_cooldown_seconds}s)"
                        ),
                    })

    # Check deployment hourly rate quota
    for i, dep in enumerate(parsed_deployments):
        dep_time = dep["timestamp"]
        # Count deployments in window [dep_time - 3600s, dep_time]
        count_in_window = sum(
            1 for d in parsed_deployments
            if 0 <= (dep_time - d["timestamp"]).total_seconds() <= 3600
        )
        if count_in_window > max_deployments_per_hour:
            quota_violations.append({
                "deployment_id": dep["deployment_id"],
                "deployments_in_hour": count_in_window,
                "max_allowed": max_deployments_per_hour,
                "message": (
                    f"Deployment {dep['deployment_id']} exceeded quota: {count_in_window} "
                    f"deployments in 1h window (max: {max_deployments_per_hour})"
                ),
            })

    passed = len(cooldown_violations) == 0 and len(quota_violations) == 0

    return {
        "schema": "termux.cooldown-quota-eval/v1",
        "passed": passed,
        "cooldown_violations": cooldown_violations,
        "quota_violations": quota_violations,
        "total_merges_evaluated": len(parsed_merges),
        "total_deployments_evaluated": len(parsed_deployments),
    }


def generate_bug_issue_payload(
    audit_findings: list[dict[str, Any]],
    pr_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Format structured GitHub issue payloads tagged with bug, skipped-review-audit, and governance."""
    labels = ["bug", "skipped-review-audit", "governance"]

    if pr_info and not audit_findings:
        pr_number = pr_info.get("number") or pr_info.get("pr_number") or "Unknown"
        title_str = f"[Governance Audit] Skipped review audit issue for PR #{pr_number}"
        body_str = (
            f"## Governance Audit Failure\n\n"
            f"Pull Request **#{pr_number}** ({pr_info.get('title', '')}) has compliance issues.\n\n"
            f"### Details\n"
            f"- **Author:** @{pr_info.get('author', 'unknown')}\n"
            f"- **URL:** {pr_info.get('url', 'N/A')}\n"
        )
    elif audit_findings:
        pr_numbers = [str(f.get("pr_number")) for f in audit_findings if f.get("pr_number")]
        pr_summary = ", #".join(pr_numbers) if pr_numbers else "Merged PRs"
        title_str = f"[Governance Audit] Skipped review audit for PR #{pr_summary}" if len(pr_numbers) == 1 else f"[Governance Audit] Skipped review audit findings ({len(audit_findings)} PRs)"

        body_lines = [
            "## Governance & Review Audit Report",
            "",
            "Automated audit detected pull requests merged with skipped reviews, missing dismissal justifications, or unaddressed feedback.",
            "",
            "### Summary of Findings",
            "",
        ]

        for finding in audit_findings:
            pr_num = finding.get("pr_number", "N/A")
            pr_title = finding.get("title", "")
            author = finding.get("author", "unknown")
            reasons = ", ".join(finding.get("findings", []))
            severity = finding.get("severity", "medium").upper()

            body_lines.append(f"#### PR #{pr_num}: {pr_title}")
            body_lines.append(f"- **Severity:** {severity}")
            body_lines.append(f"- **Author:** @{author}")
            if finding.get("url"):
                body_lines.append(f"- **URL:** {finding['url']}")
            body_lines.append(f"- **Violations:** `{reasons}`")
            body_lines.append("")

        body_lines.extend([
            "### Required Actions",
            "1. Review the implementations listed above for security, correctness, and scope.",
            "2. Provide retroactive review approval or dismissal justification in comments.",
            "3. Close this issue once governance compliance is restored.",
        ])

        body_str = "\n".join(body_lines)
    else:
        title_str = "[Governance Audit] General Governance Compliance Audit Notice"
        body_str = "No specific PR audit findings were provided."

    return {
        "title": title_str,
        "body": body_str,
        "labels": labels,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit merged PRs, cooldowns, and quotas.")
    parser.add_argument("--input", "-i", type=str, help="Path to input JSON file containing merged_prs and/or deployments")
    parser.add_argument("--mode", choices=("audit", "cooldown", "full"), default="full", help="Audit mode to run")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    input_data: dict[str, Any] = {}
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    elif not sys.stdin.isatty():
        try:
            input_data = json.load(sys.stdin)
        except Exception as exc:
            print(json.dumps({"error": f"Failed to parse stdin JSON: {exc}"}))
            return 2

    merged_prs = input_data.get("merged_prs") or []
    deployments = input_data.get("deployments") or []

    results: dict[str, Any] = {"schema": "termux.merged-branch-audit/v1"}

    if args.mode in ("audit", "full"):
        findings = audit_merged_prs(merged_prs)
        results["audit_findings"] = findings
        if findings:
            results["bug_issue_payload"] = generate_bug_issue_payload(findings)

    if args.mode in ("cooldown", "full"):
        min_cd = input_data.get("min_cooldown_seconds", 300)
        max_quota = input_data.get("max_deployments_per_hour", 5)
        results["cooldown_quota_eval"] = evaluate_cooldown_and_quotas(
            merged_prs, deployments, min_cooldown_seconds=min_cd, max_deployments_per_hour=max_quota
        )

    if args.json or not sys.stdin.isatty() or args.input:
        print(json.dumps(results, indent=2))
    else:
        print(f"Audit Completed: {len(results.get('audit_findings', []))} PR issues found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
