#!/usr/bin/env python3
from __future__ import annotations

import json
from scripts.ci.merged_branch_audit import (
    audit_merged_prs,
    evaluate_cooldown_and_quotas,
    generate_bug_issue_payload,
)


def test_audit_merged_prs_missing_justification():
    pr_data = [
        {
            "number": 101,
            "title": "Fix memory leak in buffer pool",
            "author": "alice",
            "merged": True,
            "reviews": [
                {
                    "state": "DISMISSED",
                    "user": {"login": "bob"},
                    "dismissal_justification": "",
                }
            ],
        }
    ]

    findings = audit_merged_prs(pr_data)
    assert len(findings) == 1
    assert findings[0]["pr_number"] == 101
    assert findings[0]["unjustified_dismissed_reviews"] == ["bob"]
    assert findings[0]["reason"] == "Dismissed review missing justification"


def test_audit_merged_prs_valid_justification():
    pr_data = [
        {
            "number": 102,
            "title": "Refactor router endpoints",
            "author": "charlie",
            "merged": True,
            "reviews": [
                {"state": "APPROVED", "user": {"login": "dave"}},
                {
                    "state": "DISMISSED",
                    "user": {"login": "eve"},
                    "justification": "Superseded by commit f4a2b1c",
                },
            ],
        }
    ]

    findings = audit_merged_prs(pr_data)
    assert len(findings) == 0


def test_evaluate_cooldown_and_quotas():
    events = [
        {"id": "evt1", "timestamp": "2026-10-27T10:00:00Z"},
        {"id": "evt2", "timestamp": "2026-10-27T10:02:00Z"},  # 120s later (< 300s)
        {"id": "evt3", "timestamp": "2026-10-27T10:10:00Z"},  # 480s later (>= 300s)
    ]

    report = evaluate_cooldown_and_quotas(events, cooldown_seconds=300)
    assert report["status"] == "WARNING"
    assert len(report["cooldown_violations"]) == 1
    assert report["cooldown_violations"][0]["prev_event_id"] == "evt1"
    assert report["cooldown_violations"][0]["curr_event_id"] == "evt2"
    assert report["cooldown_violations"][0]["elapsed_seconds"] == 120.0


def test_generate_bug_issue_payload():
    findings = [
        {
            "pr_number": 101,
            "title": "Fix memory leak in buffer pool",
            "author": "alice",
            "reason": "Dismissed review missing justification",
        }
    ]

    payload = generate_bug_issue_payload(findings)
    assert payload["title"] == "Governance Audit: 1 merged PR(s) skipped required review justification"
    assert "bug" in payload["labels"]
    assert "skipped-review-audit" in payload["labels"]
    assert "PR #101" in payload["body"]
    assert "@alice" in payload["body"]
