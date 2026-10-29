"""Regression tests: human feedback must suppress redundant stale nudges."""
import unittest
from datetime import datetime, timedelta, timezone

from scripts.ci.help_wanted_followup import (
    MARKER, count_prior_nudges, decide_action, filter_maintainer_activity,
    latest_approval_ts, latest_maintainer_signal, nudge_policy,
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



    def test_unearned_nudges_are_suppressed(self):
        # Focusflow #15 regression: a silent thread earns ONE base
        # nudge. Past the earned budget the loop stays silent no
        # matter how idle the thread is (it collected 10 under the
        # old self-perpetuating cooldown).
        self.assertEqual(
            decide_action(self.old_marker, None, None, self.old, self.now, total_nudges=1),
            "skip",
        )
        self.assertEqual(
            decide_action(None, None, None, self.old, self.now, total_nudges=10),
            "skip",
        )
    def test_maintainer_engagement_earns_a_followup(self):
        # One maintainer signal earns a second nudge; the doubled
        # backoff interval (144h) is satisfied by a 7-day idle.
        week = self.now - timedelta(days=7)
        self.assertEqual(
            decide_action(week, None, None, week, self.now,
                          total_nudges=1, nudges_since_signal=1, maintainer_signals=1),
            "stale_nudge",
        )
    def test_policy_backoff_doubles_with_unanswered_nudges(self):
        idle_100h = self.now - timedelta(hours=100)
        allowed, _ = nudge_policy(
            total_nudges=0, nudges_since_signal=0, maintainer_signals=0,
            first_nudge_ts=None, marker_ts=None, pr_updated=idle_100h, now=self.now)
        self.assertTrue(allowed)  # 100h > 72h base interval
        allowed, reason = nudge_policy(
            total_nudges=1, nudges_since_signal=1, maintainer_signals=1,
            first_nudge_ts=idle_100h, marker_ts=idle_100h, pr_updated=idle_100h, now=self.now)
        self.assertFalse(allowed)  # second consecutive nudge needs 144h
        self.assertIn("backoff", reason)
    def test_policy_renewal_after_long_carry(self):
        # 50 days carried since the first nudge re-earns one touch.
        allowed, _ = nudge_policy(
            total_nudges=1, nudges_since_signal=1, maintainer_signals=0,
            first_nudge_ts=self.now - timedelta(days=50),
            marker_ts=self.now - timedelta(days=30),
            pr_updated=self.now - timedelta(days=30), now=self.now)
        self.assertTrue(allowed)
    def test_policy_never_nudges_a_held_surface(self):
        allowed, reason = nudge_policy(
            total_nudges=0, nudges_since_signal=0, maintainer_signals=0,
            first_nudge_ts=None, marker_ts=None, pr_updated=self.old,
            now=self.now, held=True)
        self.assertFalse(allowed)
        self.assertIn("held", reason)
    def test_count_prior_nudges_counts_only_our_stale_nudge_markers(self):
        def comment(login, body):
            return {"user": {"login": login}, "body": body}
        comments = [
            comment("timerloggedout-spec", f"{MARKER}\n\n**Action:** `stale_nudge`"),
            comment("timerloggedout-spec", f"{MARKER}\n\n**Action:** `stale_nudge`"),
            comment("timerloggedout-spec", f"{MARKER}\n\n**Action:** `reengage`"),
            comment("someone-else", f"{MARKER}\n\n**Action:** `stale_nudge`"),
            comment("timerloggedout-spec", "A substantive update, not a follow-up marker"),
        ]
        self.assertEqual(count_prior_nudges(comments), 2)


if __name__ == "__main__":
    unittest.main()
