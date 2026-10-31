"""Regression: Tribute System 1 gates in the help-wanted lane files.

The three seed fixtures (ResQNet #53 stake PR closed as already assigned,
kdemos #26 needing a Turkish speaker, selenium-boot #180 claimed by another
contributor) must never trigger a follow-up post, a claim, or a PR.
"""
import json
import unittest
from pathlib import Path
from unittest import mock

from scripts.ci import help_wanted_claim as claim
from scripts.ci import help_wanted_contribute as contribute
from scripts.ci import help_wanted_followup as followup
from scripts.ci import help_wanted_scout as scout

FIX = Path(__file__).parent / "fixtures" / "tribute_system1"
SEEDS = sorted(FIX.glob("seed*.json"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def search_item(thread):
    s = thread["subject"]
    owner, repo = s["repo"].split("/")
    return {
        "repository_url": f"https://api.github.com/repos/{owner}/{repo}",
        "number": s["number"],
        "html_url": s["url"],
        "updated_at": "2026-10-01T00:00:00Z",
    }


class SeedFixturesNeverPost(unittest.TestCase):
    def test_three_seeds_present(self):
        self.assertEqual(len(SEEDS), 3)

    def test_gate_blocks_every_seed(self):
        for path in SEEDS:
            with self.subTest(seed=path.name):
                self.assertFalse(followup.system1_allows_post(load(path)))

    def test_unhydrated_thread_fails_closed(self):
        self.assertFalse(followup.system1_allows_post(None))

    def test_gate_allows_a_quiet_thread(self):
        quiet = {"self_login": "timerloggedout-spec",
                 "subject": {"repo": "o/r", "number": 1, "kind": "pull_request", "state": "open",
                             "url": "https://github.com/o/r/pull/1", "assignees": [], "labels": []},
                 "comments": []}
        self.assertTrue(followup.system1_allows_post(quiet))

    def test_followup_main_never_posts_for_seeds(self):
        for path in SEEDS:
            thread = load(path)
            for action in sorted(followup.GATED_ACTIONS):
                with self.subTest(seed=path.name, action=action), \
                        mock.patch.object(followup, "TOKEN", "t"), \
                        mock.patch.object(followup, "search_open_foreign_prs", return_value=[search_item(thread)]), \
                        mock.patch.object(followup, "search_closed_foreign_prs", return_value=[]), \
                        mock.patch.object(followup, "load_thread", return_value=([], [])), \
                        mock.patch.object(followup, "decide_action", return_value=action), \
                        mock.patch.object(followup, "hydrate_thread", return_value=thread), \
                        mock.patch.object(followup, "fetch_contributing", return_value=None), \
                        mock.patch.object(followup, "append_evidence") as ev, \
                        mock.patch.object(followup, "post_followup") as post:
                    self.assertEqual(followup.main(), 0)
                    post.assert_not_called()
                    kinds = [r["kind"] for r in ev.call_args[0][0]]
                    self.assertEqual(kinds, ["followup_skip_system1"])

    def test_closed_pr_gets_a_lesson_not_a_post(self):
        thread = load(FIX / "seed1_resqnet_pr53.json")
        with mock.patch.object(followup, "TOKEN", "t"), \
                mock.patch.object(followup, "search_open_foreign_prs", return_value=[]), \
                mock.patch.object(followup, "search_closed_foreign_prs", return_value=[search_item(thread)]), \
                mock.patch.object(followup, "recorded_lessons", return_value=set()), \
                mock.patch.object(followup, "hydrate_thread", return_value=thread), \
                mock.patch.object(followup, "append_evidence") as ev, \
                mock.patch.object(followup, "post_followup") as post:
            self.assertEqual(followup.main(), 0)
        post.assert_not_called()
        row = ev.call_args[0][0][0]
        self.assertEqual(row["kind"], "followup_lesson")
        self.assertEqual(row["primary"], "closed_already_assigned")


class CandidateAndPatchPreflight(unittest.TestCase):
    def issue_seeds(self):
        return [load(p) for p in SEEDS if load(p)["subject"]["kind"] == "issue"]

    def test_scout_excludes_issue_seeds(self):
        for t in self.issue_seeds():
            s = t["subject"]
            item = {"repository_url": f"https://api.github.com/repos/{s['repo']}", "number": s["number"],
                    "html_url": s["url"], "state": s["state"], "body": s.get("body"),
                    "assignees": [{"login": a} for a in s.get("assignees") or []], "labels": []}
            with self.subTest(case=t["case_id"]):
                self.assertFalse(scout.preflight(item, t["comments"])["eligible"])

    def test_scout_excludes_when_comments_unreadable(self):
        self.assertFalse(scout.preflight({"repository_url": "", "number": 1}, None)["eligible"])

    def test_claim_excludes_issue_seeds(self):
        for t in self.issue_seeds():
            s = t["subject"]
            owner, repo = s["repo"].split("/")
            meta = {"state": s["state"], "body": s.get("body"), "html_url": s["url"],
                    "assignees": [{"login": a} for a in s.get("assignees") or []], "labels": []}
            with self.subTest(case=t["case_id"]), \
                    mock.patch.object(claim, "get_comments", return_value=t["comments"]):
                self.assertFalse(claim.preflight(owner, repo, s["number"], meta)["eligible"])

    def test_stake_diff_is_refused(self):
        files = load(FIX / "seed1_resqnet_pr53.json")["files"]
        self.assertFalse(contribute.tribute_system1.preflight_pr(files)["allowed"])

    def test_contribute_without_patch_opens_nothing(self):
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "t", "HELP_WANTED_PATCH": ""}), \
                mock.patch("sys.argv", ["x", "--issue", "https://github.com/o/r/issues/1"]), \
                mock.patch.object(contribute, "_api", side_effect=AssertionError("no API call")), \
                mock.patch.object(contribute, "ensure_fork", side_effect=AssertionError("no fork")):
            self.assertEqual(contribute.main(), 0)

    def test_delivery_revalidation_blocks_closed_issue(self):
        with mock.patch.object(contribute, "_api", return_value={"state": "closed"}):
            meta, pf = contribute.revalidate_issue("o", "r", 1)
        self.assertEqual(meta["state"], "closed")
        self.assertFalse(pf["eligible"])
        self.assertIn("closed", pf["reasons"])

    def test_delivery_revalidation_fails_closed_on_unreadable_issue(self):
        with mock.patch.object(contribute, "_api", side_effect=RuntimeError("API unavailable")):
            meta, pf = contribute.revalidate_issue("o", "r", 1)
        self.assertIsNone(meta)
        self.assertFalse(pf["eligible"])
        self.assertTrue(pf["reasons"][0].startswith("issue_revalidation_failed:"))

    def test_delivery_revalidation_rechecks_assignment_preflight(self):
        current = {"state": "open", "assignees": [{"login": "another-contributor"}]}
        with mock.patch.object(contribute, "_api", return_value=current), \
                mock.patch.object(contribute, "preflight_issue",
                                  return_value={"eligible": False, "reasons": ["claimed_by_other"]}) as pf:
            meta, result = contribute.revalidate_issue("o", "r", 1)
        pf.assert_called_once_with("o", "r", 1, current)
        self.assertFalse(result["eligible"])
        self.assertEqual(result["reasons"], ["claimed_by_other"])


if __name__ == "__main__":
    unittest.main()
