#!/usr/bin/env python3
"""Unit tests for scripts/ci/merged_branch_audit.py."""

import unittest
from datetime import datetime, timezone, timedelta

from scripts.ci.merged_branch_audit import (
    audit_merged_prs,
    evaluate_cooldown_and_quotas,
    generate_bug_issue_payload,
)


class TestMergedBranchAudit(unittest.TestCase):
    def test_audit_merged_prs_valid_approval(self):
        pr = {
            "number": 101,
            "title": "Add Feature X",
            "html_url": "https://github.com/example/repo/pull/101",
            "author": "alice",
            "merged_at": "2025-01-01T12:00:00Z",
            "reviews": [
                {
                    "user": {"login": "bob", "type": "User"},
                    "state": "APPROVED",
                    "submitted_at": "2025-01-01T11:00:00Z",
                }
            ],
        }
        findings = audit_merged_prs([pr])
        self.assertEqual(len(findings), 0)

    def test_audit_merged_prs_unreviewed(self):
        pr = {
            "number": 102,
            "title": "Unreviewed Change",
            "html_url": "https://github.com/example/repo/pull/102",
            "author": "alice",
            "merged_at": "2025-01-01T12:00:00Z",
            "reviews": [],
        }
        findings = audit_merged_prs([pr])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["violation_type"], "unreviewed_implementation")
        self.assertEqual(findings[0]["pr_number"], 102)

    def test_audit_merged_prs_bot_or_author_only_reviews(self):
        pr = {
            "number": 103,
            "title": "Self approved",
            "html_url": "https://github.com/example/repo/pull/103",
            "author": "alice",
            "merged_at": "2025-01-01T12:00:00Z",
            "reviews": [
                {
                    "user": {"login": "alice", "type": "User"},
                    "state": "APPROVED",
                },
                {
                    "user": {"login": "coderabbitai[bot]", "type": "Bot"},
                    "state": "APPROVED",
                },
            ],
        }
        findings = audit_merged_prs([pr])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["violation_type"], "unreviewed_implementation")

    def test_audit_merged_prs_dismissed_review_missing_justification(self):
        pr = {
            "number": 104,
            "title": "Dismissed review without reason",
            "html_url": "https://github.com/example/repo/pull/104",
            "author": "alice",
            "merged_at": "2025-01-01T12:00:00Z",
            "reviews": [
                {
                    "user": {"login": "bob", "type": "User"},
                    "state": "DISMISSED",
                    "dismissal_justification": "   ",
                },
                {
                    "user": {"login": "charlie", "type": "User"},
                    "state": "APPROVED",
                },
            ],
        }
        findings = audit_merged_prs([pr])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["violation_type"], "missing_dismissal_justification")

    def test_audit_merged_prs_dismissed_review_with_justification(self):
        pr = {
            "number": 105,
            "title": "Dismissed review with valid reason",
            "html_url": "https://github.com/example/repo/pull/105",
            "author": "alice",
            "merged_at": "2025-01-01T12:00:00Z",
            "reviews": [
                {
                    "user": {"login": "bob", "type": "User"},
                    "state": "DISMISSED",
                    "dismissal_justification": "Superseded by architectural update in commit xyz",
                },
                {
                    "user": {"login": "charlie", "type": "User"},
                    "state": "APPROVED",
                },
            ],
        }
        findings = audit_merged_prs([pr])
        self.assertEqual(len(findings), 0)

    def test_evaluate_cooldown_and_quotas_admit(self):
        t0 = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        events = [
            {"timestamp": t0.isoformat(), "event_type": "pr_merge"},
            {"timestamp": (t0 + timedelta(seconds=400)).isoformat(), "event_type": "pr_merge"},
        ]
        res = evaluate_cooldown_and_quotas(events, min_cooldown_seconds=300, quota_limit=10, window_seconds=3600)
        self.assertEqual(res["admit"], "admit")
        self.assertEqual(len(res["violations"]), 0)

    def test_evaluate_cooldown_and_quotas_cooldown_violation(self):
        t0 = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        events = [
            {"timestamp": t0.isoformat(), "event_type": "pr_merge"},
            {"timestamp": (t0 + timedelta(seconds=100)).isoformat(), "event_type": "production_deploy"},
        ]
        res = evaluate_cooldown_and_quotas(events, min_cooldown_seconds=300, quota_limit=10, window_seconds=3600)
        self.assertEqual(res["admit"], "deny")
        self.assertTrue(any(v["violation_type"] == "cooldown_violation" for v in res["violations"]))

    def test_evaluate_cooldown_and_quotas_quota_exceeded(self):
        t0 = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        events = [
            {"timestamp": (t0 + timedelta(seconds=i * 400)).isoformat(), "event_type": "pr_merge"}
            for i in range(5)
        ]
        res = evaluate_cooldown_and_quotas(events, min_cooldown_seconds=300, quota_limit=3, window_seconds=3600)
        self.assertEqual(res["admit"], "deny")
        self.assertTrue(any(v["violation_type"] == "quota_exceeded" for v in res["violations"]))

    def test_generate_bug_issue_payload(self):
        finding = {
            "pr_number": 202,
            "pr_title": "Unreviewed critical fix",
            "html_url": "https://github.com/example/repo/pull/202",
            "author": "dave",
            "merged_at": "2025-01-01T15:00:00Z",
            "violation_type": "unreviewed_implementation",
            "reason": "PR #202 was merged without any human approving reviews",
        }
        payload = generate_bug_issue_payload(finding)
        self.assertIn("Audit Violation: Unreviewed Implementation on PR #202", payload["title"])
        self.assertIn("PR #202 was merged without any human approving reviews", payload["body"])
        self.assertEqual(payload["labels"], ["bug", "skipped-review-audit", "governance"])


if __name__ == "__main__":
    unittest.main()
