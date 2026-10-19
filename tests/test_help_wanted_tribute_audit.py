"""Tests for automated Help-Wanted tribute lifecycle auditing."""
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ci.help_wanted_tribute_audit import audit_one, parse_pr_url


class HelpWantedTributeAuditTests(unittest.TestCase):
    def test_hourly_status_refresh_runs_and_publishes_audit(self):
        workflow = Path(".github/workflows/help-wanted-status-refresh.yml").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/ci/help_wanted_tribute_audit.py", workflow)
        self.assertIn("docs/ops/generated/help-wanted-tribute-audit.json", workflow)

    def test_parse_canonical_pull_request_url(self):
        self.assertEqual(
            parse_pr_url("https://github.com/example/project/pull/42"),
            ("example", "project", 42),
        )
        self.assertIsNone(parse_pr_url("https://github.com/example/project/issues/42"))

    @patch("scripts.ci.help_wanted_tribute_audit.api_get")
    def test_validated_solution_requires_diff_proof_and_successful_checks(self, api_get):
        api_get.side_effect = [
            ({
                "state": "open",
                "merged_at": None,
                "body": "### Help-Given Tribute\n- Stage: solution\n- Diff proof: verified\n- Validation: pytest passed",
                "head": {"sha": "abc123"},
                "base": {"sha": "def456"},
            }, None),
            ([{"filename": "src/fix.py", "additions": 10, "deletions": 2}], None),
            ({"check_runs": [{"status": "completed", "conclusion": "success"}]}, None),
        ]
        result = audit_one("https://github.com/example/project/pull/42")
        self.assertEqual(result["stage"], "validated_solution")
        self.assertTrue(result["checks_pass"])
        self.assertFalse(result["realized_effect_verified"])

    @patch("scripts.ci.help_wanted_tribute_audit.api_get")
    def test_skipped_checks_without_success_do_not_validate(self, api_get):
        api_get.side_effect = [
            ({
                "state": "open", "merged_at": None,
                "body": "### Help-Given Tribute\n- Stage: solution\n- Diff proof: verified\n- Validation: skipped",
                "head": {"sha": "abc123"}, "base": {"sha": "def456"},
            }, None),
            ([{"filename": "src/fix.py", "additions": 2, "deletions": 0}], None),
            ({"total_count": 2, "check_runs": [
                {"status": "completed", "conclusion": "skipped"},
                {"status": "completed", "conclusion": "neutral"},
            ]}, None),
        ]
        result = audit_one("https://github.com/example/project/pull/42")
        self.assertFalse(result["checks_pass"])
        self.assertEqual(result["stage"], "solution_claimed_unvalidated")

    @patch("scripts.ci.help_wanted_tribute_audit.api_get")
    def test_truncated_check_run_response_is_an_evidence_gap(self, api_get):
        api_get.side_effect = [
            ({
                "state": "open", "merged_at": None,
                "body": "### Help-Given Tribute\n- Stage: solution\n- Diff proof: verified\n- Validation: pytest passed",
                "head": {"sha": "abc123"}, "base": {"sha": "def456"},
            }, None),
            ([{"filename": "src/fix.py", "additions": 2, "deletions": 0}], None),
            ({"total_count": 101, "check_runs": [
                {"status": "completed", "conclusion": "success"},
            ]}, None),
        ]
        result = audit_one("https://github.com/example/project/pull/42")
        self.assertTrue(result["checks_truncated"])
        self.assertFalse(result["checks_complete"])
        self.assertFalse(result["checks_pass"])
        self.assertIn("checks_truncated", result["evidence_gaps"])

    @patch("scripts.ci.help_wanted_tribute_audit.api_get")
    def test_stake_only_is_not_a_solution(self, api_get):
        api_get.side_effect = [
            ({
                "state": "open",
                "merged_at": None,
                "body": "stake only",
                "head": {"sha": "abc123"},
                "base": {"sha": "def456"},
            }, None),
            ([{"filename": ".github/help-wanted-lane-stake.md", "additions": 1, "deletions": 0}], None),
            ({"check_runs": []}, None),
        ]
        result = audit_one("https://github.com/example/project/pull/42")
        self.assertEqual(result["stage"], "stake_only")
        self.assertFalse(result["checks_pass"])

    @patch("scripts.ci.help_wanted_tribute_audit.api_get")
    def test_rate_limit_is_unknown_not_success(self, api_get):
        api_get.return_value = (None, "rate_limited")
        result = audit_one("https://github.com/example/project/pull/42")
        self.assertEqual(result["stage"], "unknown")
        self.assertEqual(result["audit_status"], "deferred")
        self.assertFalse(result["realized_effect_verified"])

    @patch("scripts.ci.help_wanted_tribute_audit.api_get")
    def test_merged_pr_does_not_imply_realized_effect(self, api_get):
        api_get.side_effect = [
            ({
                "state": "closed",
                "merged_at": "2026-10-18T10:00:00Z",
                "body": "merged",
                "head": {"sha": "abc123"},
                "base": {"sha": "def456"},
            }, None),
            ([{"filename": "src/fix.py", "additions": 2, "deletions": 1}], None),
            ({"check_runs": [{"status": "completed", "conclusion": "success"}]}, None),
        ]
        result = audit_one("https://github.com/example/project/pull/42")
        self.assertEqual(result["stage"], "accepted")
        self.assertFalse(result["realized_effect_verified"])
        self.assertIn("independently verified effect receipt", result["realization_note"])


if __name__ == "__main__":
    unittest.main()
