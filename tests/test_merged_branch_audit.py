"""Unit tests for scripts/ci/merged_branch_audit.py."""
from __future__ import annotations

import json
import subprocess
import sys
from unittest.mock import patch

import pytest

from scripts.ci.merged_branch_audit import (
    audit_merged_prs,
    evaluate_cooldown_and_quotas,
    generate_bug_issue_payload,
    main,
)


def test_audit_merged_prs_clean():
    merged_prs = [
        {
            "number": 101,
            "title": "Fix widget layout",
            "author": "alice",
            "url": "https://github.com/test/repo/pull/101",
            "head_sha": "sha123",
            "reviews": [
                {
                    "user": {"login": "bob", "type": "User"},
                    "commit_id": "sha123",
                    "state": "APPROVED",
                    "submitted_at": "2025-01-01T10:00:00Z",
                }
            ],
        }
    ]
    findings = audit_merged_prs(merged_prs)
    assert len(findings) == 0


def test_audit_merged_prs_unreviewed():
    merged_prs = [
        {
            "number": 102,
            "title": "Unreviewed patch",
            "author": "charlie",
            "url": "https://github.com/test/repo/pull/102",
            "head_sha": "sha456",
            "reviews": [],
        }
    ]
    findings = audit_merged_prs(merged_prs)
    assert len(findings) == 1
    assert findings[0]["pr_number"] == 102
    assert "unreviewed_implementation" in findings[0]["findings"]
    assert findings[0]["severity"] == "high"


def test_audit_merged_prs_missing_dismissal_justification():
    merged_prs = [
        {
            "number": 103,
            "title": "Dismissed review patch",
            "author": "dave",
            "url": "https://github.com/test/repo/pull/103",
            "head_sha": "sha789",
            "reviews": [
                {
                    "user": {"login": "bob", "type": "User"},
                    "commit_id": "sha789",
                    "state": "APPROVED",
                    "submitted_at": "2025-01-01T10:00:00Z",
                },
                {
                    "user": {"login": "eve", "type": "User"},
                    "commit_id": "sha789",
                    "state": "DISMISSED",
                    "dismissal_justification": "",
                },
            ],
        }
    ]
    findings = audit_merged_prs(merged_prs)
    assert len(findings) == 1
    assert "missing_dismissal_justification" in findings[0]["findings"]


def test_audit_merged_prs_changes_requested():
    merged_prs = [
        {
            "number": 104,
            "title": "PR with open changes requested",
            "author": "frank",
            "url": "https://github.com/test/repo/pull/104",
            "head_sha": "sha999",
            "reviews": [
                {
                    "user": {"login": "grace", "type": "User"},
                    "commit_id": "sha999",
                    "state": "CHANGES_REQUESTED",
                    "submitted_at": "2025-01-01T10:00:00Z",
                }
            ],
        }
    ]
    findings = audit_merged_prs(merged_prs)
    assert len(findings) == 1
    assert "missed_review_implementation" in findings[0]["findings"]


def test_evaluate_cooldown_and_quotas_compliant():
    merged_prs = [
        {"number": 1, "merged_at": "2025-01-01T10:00:00Z"}
    ]
    deployments = [
        {"id": "dep-1", "created_at": "2025-01-01T10:10:00Z"}  # 600s after merge (>300s)
    ]
    res = evaluate_cooldown_and_quotas(merged_prs, deployments, min_cooldown_seconds=300, max_deployments_per_hour=5)
    assert res["passed"] is True
    assert len(res["cooldown_violations"]) == 0
    assert len(res["quota_violations"]) == 0


def test_evaluate_cooldown_and_quotas_violations():
    merged_prs = [
        {"number": 2, "merged_at": "2025-01-01T12:00:00Z"}
    ]
    # Deployment occurs 60s after merge (violates 300s min_cooldown)
    # Also 6 deployments in 1 hour window (violates max 5/hr)
    deployments = [
        {"id": f"dep-{i}", "created_at": f"2025-01-01T12:0{i}:00Z"}
        for i in range(1, 7)
    ]
    res = evaluate_cooldown_and_quotas(merged_prs, deployments, min_cooldown_seconds=300, max_deployments_per_hour=5)
    assert res["passed"] is False
    assert len(res["cooldown_violations"]) > 0
    assert len(res["quota_violations"]) > 0


def test_generate_bug_issue_payload():
    findings = [
        {
            "pr_number": 201,
            "title": "Buggy feature merge",
            "author": "helen",
            "url": "https://github.com/test/repo/pull/201",
            "findings": ["unreviewed_implementation"],
            "severity": "high",
        }
    ]
    payload = generate_bug_issue_payload(findings)
    assert payload["labels"] == ["bug", "skipped-review-audit", "governance"]
    assert "[Governance Audit]" in payload["title"]
    assert "201" in payload["title"]
    assert "Buggy feature merge" in payload["body"]
    assert "@helen" in payload["body"]


def test_main_cli(tmp_path):
    input_file = tmp_path / "input.json"
    data = {
        "merged_prs": [
            {
                "number": 300,
                "title": "Test PR",
                "author": "ian",
                "reviews": [],
                "merged_at": "2025-01-01T12:00:00Z",
            }
        ],
        "deployments": [],
    }
    input_file.write_text(json.dumps(data), encoding="utf-8")

    test_args = ["merged_branch_audit.py", "--input", str(input_file), "--json"]
    with patch.object(sys, "argv", test_args):
        assert main() == 0
