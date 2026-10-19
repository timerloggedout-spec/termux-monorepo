"""Regression tests: human feedback must suppress redundant stale nudges."""
import unittest
from datetime import datetime, timedelta, timezone

from scripts.ci.help_wanted_followup import (
    decide_action, filter_maintainer_activity, latest_approval_ts, latest_maintainer_signal,
)


class HelpWantedFollowupPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 18, 12, 0, tzinfo=timezone.utc)
        self.old = self.now - timedelta(days=5)
        self.recent_marker = self.now - timedelta(hours=2)
        self.old_marker = self.now - timedelta(days=4)

    def test_stale_nudge_only_when_no_maintainer_feedback_exists(self):
        self.assertEqual(
            decide_action(None, None, None, self.old, self.now),
            "stale_nudge",
        )

    def test_prior_maintainer_feedback_suppresses_stale_nudge(self):
        feedback = self.now - timedelta(days=4, hours=1)
        self.assertEqual(
            decide_action(self.old_marker, feedback, None, self.old, self.now),
            "skip",
        )

    def test_new_feedback_after_marker_reengages_after_cooldown(self):
        feedback = self.now - timedelta(hours=20)
        marker = self.now - timedelta(days=2)
        self.assertEqual(
            decide_action(marker, feedback, None, self.old, self.now),
            "reengage",
        )

    def test_recent_feedback_does_not_fall_through_to_stale_nudge(self):
        feedback = self.now - timedelta(hours=1)
        marker = self.now - timedelta(hours=1, minutes=30)
        self.assertEqual(
            decide_action(marker, feedback, None, self.old, self.now),
            "skip",
        )

    def test_participant_and_unknown_association_activity_is_filtered(self):
        comments = [
            {"author_association": "NONE", "body": "A participant comment"},
            {"author_association": "OWNER", "body": "Maintainer guidance"},
            {"body": "Missing association is not trusted"},
        ]
        reviews = [
            {"author_association": "CONTRIBUTOR", "state": "CHANGES_REQUESTED"},
            {"author_association": "MEMBER", "state": "COMMENTED"},
        ]
        filtered_comments, filtered_reviews = filter_maintainer_activity(comments, reviews)
        self.assertEqual([c["body"] for c in filtered_comments], ["Maintainer guidance"])
        self.assertEqual([r["state"] for r in filtered_reviews], ["COMMENTED"])

    def test_empty_body_maintainer_approval_suppresses_stale_nudge(self):
        approval = self.now - timedelta(days=3)
        self.assertEqual(
            decide_action(None, None, None, self.old, self.now, approval_ts=approval),
            "skip",
        )

    def test_approval_after_marker_does_not_trigger_reengagement(self):
        approval = self.now - timedelta(hours=1)
        marker = self.now - timedelta(days=2)
        self.assertEqual(
            decide_action(marker, None, None, self.old, self.now, approval_ts=approval),
            "skip",
        )
        reviews = [{
            "author_association": "OWNER",
            "state": "APPROVED",
            "submitted_at": "2026-10-18T10:00:00Z",
            "body": "",
        }]
        _, trusted_reviews = filter_maintainer_activity([], reviews)
        self.assertEqual(latest_approval_ts(trusted_reviews), datetime(2026, 10, 18, 10, 0, tzinfo=timezone.utc))
        self.assertEqual(latest_maintainer_signal([], trusted_reviews, "example")[0], None)

    def test_changes_requested_after_marker_keeps_priority(self):
        changes = self.now - timedelta(hours=3)
        marker = self.now - timedelta(hours=5)
        self.assertEqual(
            decide_action(marker, None, changes, self.old, self.now),
            "changes",
        )


if __name__ == "__main__":
    unittest.main()
