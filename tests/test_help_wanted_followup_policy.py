"""Regression tests: human feedback must suppress redundant stale nudges."""
import unittest
from datetime import datetime, timedelta, timezone

from scripts.ci.help_wanted_followup import decide_action


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

    def test_changes_requested_after_marker_keeps_priority(self):
        changes = self.now - timedelta(hours=3)
        marker = self.now - timedelta(hours=5)
        self.assertEqual(
            decide_action(marker, None, changes, self.old, self.now),
            "changes",
        )


if __name__ == "__main__":
    unittest.main()
