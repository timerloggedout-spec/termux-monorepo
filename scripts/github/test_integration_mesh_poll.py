#!/usr/bin/env python3
"""Unit tests for the integration mesh poll diff/plan-state logic (pure parts)."""
import unittest

from integration_mesh_poll import diff_snapshots, name_set, render_comment


def snap(**kw):
    base = {
        "check_apps_30": {"github-actions": {"suites": 10}},
        "cross_repo_apps": {"github-actions": {"name": "Actions", "repo_count": 7, "repos": []}},
        "org_installations": {"Research-Astute": ["render"], "search-astute-ly": ["mintlify"]},
        "hooks": [{"host": "example.com", "active": True, "events": 3, "last_code": 200}],
        "secrets": {"repo_actions": {"total": 1, "names": ["A_TOKEN"]}},
        "environments": ["Production"],
        "variables": ["DEVICE_QUEUE_URL"],
        "workflows": {"total": 200, "active": 199, "names": ["a"]},
        "stale_rows": [],
        "prs_total": 1300,
        "issues_total_true": 200,
        "codespaces_total": 3,
        "comment_actors": [{"login": "owner", "type": "User", "comments": 5}],
        "deployment_creators": {"vercel[bot]": 9},
        "degraded": [],
        "figure_counter": 0,
    }
    base.update(kw)
    return base


class DiffTests(unittest.TestCase):
    def test_no_change_no_lines(self):
        s, f = diff_snapshots(snap(), snap())
        self.assertEqual((s, f), ([], []))

    def test_new_check_app_is_structural(self):
        cur = snap(check_apps_30={"github-actions": {"suites": 9}, "buildkite": {"suites": 2}})
        s, f = diff_snapshots(snap(), cur)
        self.assertTrue(any("buildkite" in x for x in s))
        self.assertEqual(f, [])

    def test_secret_name_change_is_structural(self):
        cur = snap(secrets={"repo_actions": {"total": 2, "names": ["A_TOKEN", "B_TOKEN"]}})
        s, _ = diff_snapshots(snap(), cur)
        self.assertTrue(any("B_TOKEN" in x for x in s))

    def test_figure_moves_are_not_structural(self):
        cur = snap(prs_total=1310, issues_total_true=205)
        s, f = diff_snapshots(snap(), cur)
        self.assertEqual(s, [])
        self.assertEqual(len(f), 2)

    def test_degraded_section_never_reports_removals(self):
        cur = snap(check_apps_30=None, secrets={"repo_actions": {"_error_status": 403}})
        s, f = diff_snapshots(snap(), cur)
        self.assertEqual((s, f), ([], []))

    def test_webhook_health_flip_is_structural(self):
        cur = snap(hooks=[{"host": "example.com", "active": True, "events": 3, "last_code": 400}])
        s, _ = diff_snapshots(snap(), cur)
        self.assertTrue(any("webhooks" in x for x in s))

    def test_new_stale_row_is_structural(self):
        cur = snap(stale_rows=["§9 row references #1491 as open/pending but it is closed"])
        s, _ = diff_snapshots(snap(), cur)
        self.assertTrue(any("stale plan row" in x for x in s))

    def test_name_set(self):
        self.assertEqual(name_set({"names": ["B", "A"]}), ["A", "B"])
        self.assertIsNone(name_set({"_error_status": 403}))

    def test_comment_renders_sections(self):
        body = render_comment(snap(), ["x structural"], ["y figure"], 2, "https://example/run")
        self.assertIn("Structural changes", body)
        self.assertIn("2/4", body)
        self.assertIn("[MUSEai]", body)


if __name__ == "__main__":
    unittest.main()
