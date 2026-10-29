"""Operational receipts must not be counted as successful tributes."""
import unittest
from pathlib import Path

from unittest.mock import patch

from scripts.ci import help_wanted_status
from scripts.ci.help_wanted_status import (
    build_tributes,
    classify_receipt_outcome,
    is_own_repo,
    live_foreign_prs,
)


class HelpWantedStatusOutcomeTests(unittest.TestCase):
    def test_skip_is_skipped_not_successful_work(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_skip_cooldown", "ok": True, "action": "skip"}),
            "skipped",
        )

    def test_successful_action_is_actioned_not_accepted(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_stale_nudge", "ok": True, "action": "stale_nudge"}),
            "actioned",
        )

    def test_failed_action_is_failed(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_changes", "ok": False, "action": "changes"}),
            "failed",
        )

    def test_failed_skip_receipt_is_not_hidden_as_skipped(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_skip_cooldown", "ok": False, "action": "skip"}),
            "failed",
        )

    def test_dashboard_exposes_audited_stages_and_operational_outcomes(self):
        html = Path("apps/help-wanted-dashboard/index.html").read_text(encoding="utf-8")
        self.assertIn("Validated (audited)", html)
        self.assertIn("Accepted (audited)", html)
        self.assertIn("Realized effects (sample)", html)
        self.assertIn("out.skipped", html)
        self.assertIn("out.failed", html)
        self.assertIn("audit.not_audited_count", html)
        self.assertIn("audit.audited_this_run_count", html)
        self.assertIn("audit.partial_this_run_count", html)
        self.assertIn("audit.deferred_this_run_count", html)
        self.assertIn("audit.unknown_this_run_count", html)
        self.assertIn("audit.attempted_this_run_count", html)
        workflow = Path(".github/workflows/help-wanted-telemetry-tests.yml").read_text(encoding="utf-8")
        pull_request_paths = workflow.split("  pull_request:", 1)[1].split("  push:", 1)[0]
        push_paths = workflow.split("  push:", 1)[1].split("  workflow_dispatch:", 1)[0]
        for path in (
            ".github/workflows/help-wanted-telemetry-tests.yml",
            "docs/ops/AUTOMATED-TELEMETRY-AUDIT.md",
            "docs/ops/HELP-WANTED-REALIZATION-EVIDENCE.md",
        ):
            self.assertIn(path, pull_request_paths)
            self.assertIn(path, push_paths)


class HelpWantedStatusTributeScopeTests(unittest.TestCase):
    """Tributes are foreign-only: our own repos must never be listed."""

    def test_is_own_repo_matches_author_owned_repos(self):
        self.assertTrue(is_own_repo("timerloggedout-spec/termux-monorepo"))
        self.assertTrue(is_own_repo("timerloggedout-spec/timerloggedout-spec.github.io"))
        self.assertTrue(is_own_repo("TimerLoggedOut-Spec/gh-aw_fork"))
        self.assertFalse(is_own_repo("E-Timileyin/Sail-CLI"))
        self.assertFalse(is_own_repo(""))
        self.assertFalse(is_own_repo("no-slash"))

    def test_live_own_repo_prs_are_not_tributes(self):
        foreign_closed = [
            {
                "html_url": "https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/pull/5",
                "repo": "timerloggedout-spec/timerloggedout-spec.github.io",
                "number": 5,
                "title": "Partners grid: render link-only referral programmes (Neon)",
                "state": "closed",
                "updated_at": "2026-10-28T21:19:38Z",
            },
            {
                "html_url": "https://github.com/E-Timileyin/Sail-CLI/pull/23",
                "repo": "E-Timileyin/Sail-CLI",
                "number": 23,
                "title": "foreign pr",
                "state": "closed",
                "updated_at": "2026-10-20T00:00:00Z",
            },
        ]
        tributes = build_tributes([], [], foreign_closed)
        self.assertEqual(
            [t["pr_url"] for t in tributes],
            ["https://github.com/E-Timileyin/Sail-CLI/pull/23"],
        )

    def test_receipt_rows_for_own_repos_are_not_tributes(self):
        rows = [
            {
                "pr_url": "https://github.com/timerloggedout-spec/gh-aw_fork/pull/2",
                "kind": "followup_lesson",
                "ok": True,
                "ts": "2026-10-22T11:50:12Z",
            },
            {
                "pr_url": "https://github.com/timerloggedout-spec/termux-monorepo/pull/1",
                "kind": "upstream_pr",
                "ok": True,
                "ts": "2026-10-22T11:50:12Z",
            },
            {
                "pr_url": "https://github.com/Kilo-Org/agentic-path/pull/26",
                "kind": "followup_stale_nudge",
                "ok": True,
                "ts": "2026-10-21T00:00:00Z",
            },
        ]
        tributes = build_tributes(rows, [], [])
        self.assertEqual(
            [t["pr_url"] for t in tributes],
            ["https://github.com/Kilo-Org/agentic-path/pull/26"],
        )


def _search_item(repo, number):
    return {
        "repository_url": f"https://api.github.com/repos/{repo}",
        "html_url": f"https://github.com/{repo}/pull/{number}",
        "title": f"pr {number}",
        "number": number,
        "updated_at": "2026-10-01T00:00:00Z",
    }


class HelpWantedLiveForeignPaginationTests(unittest.TestCase):
    """The ledger census must walk every search page, not one window."""

    def test_walks_all_pages_and_filters_own_repos_on_later_pages(self):
        pages = {
            1: [_search_item("foreign-owner/repo-a", n) for n in range(1, 101)],
            2: [
                _search_item("foreign-owner/repo-b", 1),
                _search_item("timerloggedout-spec/timerloggedout-spec.github.io", 6),
                _search_item("foreign-owner/repo-c", 2),
            ],
        }
        requested = []

        def fake_api_get(path):
            page = int(path.split("&page=")[1].split("&")[0])
            requested.append(page)
            return {"items": pages.get(page, []), "total_count": 103}

        with patch.object(help_wanted_status, "api_get", fake_api_get):
            out = live_foreign_prs("closed")
        self.assertEqual(requested, [1, 2])
        self.assertEqual(len(out), 102)
        self.assertTrue(all(not is_own_repo(r["repo"]) for r in out))
        self.assertTrue(all(r["state"] == "closed" for r in out))

    def test_api_failure_keeps_pages_already_fetched(self):
        def flaky_api_get(path):
            if "&page=1&" in path:
                return {
                    "items": [_search_item("foreign-owner/repo-a", n) for n in range(1, 101)],
                    "total_count": 150,
                }
            return None

        with patch.object(help_wanted_status, "api_get", flaky_api_get):
            out = live_foreign_prs("open")
        self.assertEqual(len(out), 100)


if __name__ == "__main__":
    unittest.main()
