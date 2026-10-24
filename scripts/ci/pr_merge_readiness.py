#!/usr/bin/env python3
"""Fail-closed decision engine for the governed PR auto-merge workflow."""
from __future__ import annotations
import json, sys
from datetime import datetime
from typing import Any

def _parse_time(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return value

def evaluate(snapshot: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    protection = snapshot.get("protection") or {}
    pr = snapshot.get("pr") or {}
    reviews = snapshot.get("reviews") or []
    if snapshot.get("enabled") is not True:
        reasons.append("GOVERNED_AUTO_MERGE_ENABLED is not true")
    if protection.get("unavailable") is True:
        reasons.append("branch protection could not be verified")
    required_reviews = protection.get("required_pull_request_reviews") or {}
    required_approvals = required_reviews.get("required_approving_review_count", 0)
    if not isinstance(required_approvals, int) or required_approvals < 1:
        reasons.append("branch protection does not require at least one approval")
    if not (required_reviews.get("dismiss_stale_reviews") is True or required_reviews.get("require_last_push_approval") is True):
        reasons.append("stale approvals are not safely invalidated")
    checks = protection.get("required_status_checks") or {}
    required_checks = checks.get("contexts") or [
        item.get("context") for item in (checks.get("checks") or [])
        if isinstance(item, dict) and item.get("context")
    ]
    if not required_checks:
        reasons.append("no required status checks are configured")
    if (protection.get("required_conversation_resolution") or {}).get("enabled") is not True:
        reasons.append("required conversation resolution is not enabled")
    if not pr.get("number"):
        reasons.append("pull request number is missing")
    if pr.get("state", "OPEN") != "OPEN":
        reasons.append("pull request is not open")
    if pr.get("draft") is True:
        reasons.append("pull request is a draft")
    if "automerge:eligible" not in (pr.get("labels") or []):
        reasons.append("automerge:eligible label is missing")
    if pr.get("merge_state") != "CLEAN":
        reasons.append("pull request is not in a clean merge state")
    head_sha = pr.get("head_sha")
    if not head_sha:
        reasons.append("current pull request head SHA is missing")
    latest_by_reviewer: dict[str, dict[str, Any]] = {}
    for review in reviews:
        user = review.get("user") or {}
        login = str(user.get("login") or "").lower()
        if not login or user.get("type") == "Bot" or login == str(pr.get("author") or "").lower():
            continue
        # Old-head reviews must not count as approvals or erase a current-head
        # change request merely because the old-head review was submitted later.
        if review.get("commit_id") != head_sha:
            continue
        if review.get("state") == "PENDING" or not review.get("submitted_at"):
            continue
        prior = latest_by_reviewer.get(login)
        if prior is None or _parse_time(review.get("submitted_at")) >= _parse_time(prior.get("submitted_at")):
            latest_by_reviewer[login] = review
    for review in reviews:
        if review.get("state") == "DISMISSED":
            justification = (review.get("dismissal_justification") or review.get("justification") or "").strip()
            if not justification:
                reasons.append("dismissed review missing explicit dismissal justification")
                break
    current_reviews = list(latest_by_reviewer.values())
    if any(review.get("state") == "CHANGES_REQUESTED" for review in current_reviews):
        reasons.append("a current-head human review requests changes")
    approvals = sum(1 for review in current_reviews if review.get("state") == "APPROVED")
    if isinstance(required_approvals, int) and approvals < required_approvals:
        reasons.append(f"current-head human approvals {approvals} < required {required_approvals}")
    return {
        "schema": "termux.pr-merge-readiness/v1",
        "decision": "enable_auto_merge" if not reasons else "wait",
        "pr_number": pr.get("number"),
        "head_sha": head_sha,
        "human_current_head_approvals": approvals,
        "required_approvals": required_approvals if isinstance(required_approvals, int) else None,
        "required_check_count": len(required_checks),
        "reasons": reasons,
    }

def main() -> int:
    try:
        snapshot = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError) as exc:
        print(json.dumps({"schema": "termux.pr-merge-readiness/v1", "decision": "wait", "reasons": [f"invalid input: {exc}"]}))
        return 2
    print(json.dumps(evaluate(snapshot), sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
