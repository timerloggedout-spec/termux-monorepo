import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts" / "ci"))
from pr_merge_readiness import evaluate

def eligible_snapshot():
    return {
        "enabled": True,
        "protection": {
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_last_push_approval": False,
            },
            "required_status_checks": {"contexts": ["repo-gate", "workflow-surface-policy"]},
            "required_conversation_resolution": {"enabled": True},
        },
        "pr": {
            "number": 42, "state": "OPEN", "draft": False, "author": "contributor",
            "labels": ["automerge:eligible"], "merge_state": "CLEAN", "head_sha": "abc123",
        },
        "reviews": [{
            "user": {"login": "reviewer", "type": "User"}, "state": "APPROVED",
            "submitted_at": "2026-10-19T12:00:00Z", "commit_id": "abc123",
        }],
    }

class MergeReadinessTests(unittest.TestCase):
    def test_eligible_snapshot_enables_auto_merge(self):
        result = evaluate(eligible_snapshot())
        self.assertEqual(result["decision"], "enable_auto_merge")
        self.assertEqual(result["human_current_head_approvals"], 1)
    def test_disabled_switch_fails_closed(self):
        snapshot = eligible_snapshot(); snapshot["enabled"] = False
        self.assertEqual(evaluate(snapshot)["decision"], "wait")
    def test_missing_protection_fails_closed(self):
        snapshot = eligible_snapshot(); snapshot["protection"] = {"unavailable": True}
        self.assertEqual(evaluate(snapshot)["decision"], "wait")
    def test_missing_current_head_approval_fails_closed(self):
        snapshot = eligible_snapshot(); snapshot["reviews"][0]["commit_id"] = "oldsha"
        self.assertEqual(evaluate(snapshot)["decision"], "wait")
    def test_bot_and_author_approvals_do_not_count(self):
        snapshot = eligible_snapshot()
        snapshot["reviews"] = [
            {"user": {"login": "bot", "type": "Bot"}, "state": "APPROVED", "submitted_at": "2026-10-19T12:00:00Z", "commit_id": "abc123"},
            {"user": {"login": "contributor", "type": "User"}, "state": "APPROVED", "submitted_at": "2026-10-19T12:01:00Z", "commit_id": "abc123"},
        ]
        self.assertEqual(evaluate(snapshot)["decision"], "wait")
    def test_latest_review_replaces_older_approval(self):
        snapshot = eligible_snapshot()
        snapshot["reviews"].append({"user": {"login": "reviewer", "type": "User"}, "state": "CHANGES_REQUESTED", "submitted_at": "2026-10-19T12:05:00Z", "commit_id": "abc123"})
        result = evaluate(snapshot)
        self.assertEqual(result["decision"], "wait")
        self.assertTrue(any("requests changes" in reason for reason in result["reasons"]))
    def test_missing_required_checks_blocks(self):
        snapshot = eligible_snapshot(); snapshot["protection"]["required_status_checks"] = None
        self.assertEqual(evaluate(snapshot)["decision"], "wait")
    def test_unresolved_conversation_policy_blocks(self):
        snapshot = eligible_snapshot(); snapshot["protection"]["required_conversation_resolution"] = {"enabled": False}
        self.assertEqual(evaluate(snapshot)["decision"], "wait")
    def test_missing_eligibility_label_blocks(self):
        snapshot = eligible_snapshot(); snapshot["pr"]["labels"] = []
        self.assertEqual(evaluate(snapshot)["decision"], "wait")

if __name__ == "__main__":
    unittest.main()
