"""QDesk self-repair loop: pure decision functions (no network)."""
import unittest

from scripts.que import self_repair as sr


class Signature(unittest.TestCase):
    def test_ids_and_numbers_do_not_split_signatures(self):
        a = sr.signature("HttpError: API rate limit exceeded for installation. request ID CC40:360224:32FF226 and timestamp 2026-11-12 09:51:00 UTC")
        b = sr.signature("HttpError: API rate limit exceeded for installation. request ID FE84:121B21:AD5919 and timestamp 2026-11-11 01:02:03 UTC")
        self.assertEqual(a, b)

    def test_different_errors_differ(self):
        self.assertNotEqual(sr.signature("exit code 1 in Census vs baseline"),
                            sr.signature("Commenting is disabled on issues with more than 2500 comments"))


class Routing(unittest.TestCase):
    def test_delphi_owned_elsewhere(self):
        self.assertEqual(sr.owner_room("delphi-rfp-feed-collect", ".github/workflows/delphi-rfp-feed-collect.yml"), "delphi-room")
        self.assertEqual(sr.owner_room("proposal-lifecycle", "x"), "delphi-room")
        self.assertIsNone(sr.owner_room("repo gate", ".github/workflows/repo-gate.yml"))

    def test_branch_gates_rank_first(self):
        self.assertGreater(sr.priority(2, 10, ".github/workflows/repo-gate.yml"),
                           sr.priority(5, 10, ".github/workflows/other.yml"))

    def test_dedupe_key_is_workflow_and_signature(self):
        self.assertEqual(sr.item_key(".github/workflows/repo-gate.yml", "abc"), "repo-gate.yml:abc")
        body = sr.item_body({"key": "repo-gate.yml:abc", "path": "p", "sig": "abc", "priority": 1, "failures": 1,
                             "total": 1, "window_h": 6, "step": "s", "message": "m",
                             "receipts": [{"url": "https://x/runs/1", "sha": "0123456789"}]})
        self.assertIn("que-self-repair-key: repo-gate.yml:abc -->", body)


GREEN = [{"name": "ci", "status": "completed", "conclusion": "success"}]
ADD = [{"filename": "scripts/x.py", "status": "modified", "patch": "+print(1)"}]


class Promote(unittest.TestCase):
    def test_self_merge_needs_green_two_candidates_and_outside_doe(self):
        d = sr.promote_decision(ADD, GREEN, 2, ["doe-reviewer"], "swarm[bot]")
        self.assertEqual(d["action"], "self_merge")

    def test_one_candidate_waits(self):
        self.assertEqual(sr.promote_decision(ADD, GREEN, 1, ["doe"], "a")["action"], "wait")

    def test_author_cannot_be_own_doe(self):
        self.assertEqual(sr.promote_decision(ADD, GREEN, 2, ["swarm[bot]"], "swarm[bot]")["action"], "wait")

    def test_red_or_pending_waits(self):
        red = [{"name": "ci", "status": "completed", "conclusion": "failure"}]
        self.assertEqual(sr.promote_decision(ADD, red, 2, ["d"], "a")["action"], "wait")
        pend = [{"name": "ci", "status": "in_progress"}]
        self.assertEqual(sr.promote_decision(ADD, pend, 2, ["d"], "a")["action"], "wait")

    def test_destructive_secrets_money_go_to_owner(self):
        rm = [{"filename": "old.py", "status": "removed", "patch": ""}]
        self.assertEqual(sr.promote_decision(rm, GREEN, 2, ["d"], "a")["action"], "owner_packet")
        sec = [{"filename": "w.yml", "status": "modified", "patch": "+  KEY: ${{ secrets.NEW_TOKEN }}"}]
        self.assertEqual(sr.promote_decision(sec, GREEN, 2, ["d"], "a")["action"], "owner_packet")
        money = [{"filename": "b.py", "status": "modified", "patch": "+raise spend-limit"}]
        self.assertEqual(sr.promote_decision(money, GREEN, 2, ["d"], "a")["action"], "owner_packet")


class Learn(unittest.TestCase):
    def test_verified_steps_weight_once(self):
        items = [{"number": 7, "labels": [{"name": "sr:verified"}, {"name": "role:builder"}, {"name": "class:rate-limit"}]}]
        w, changed = sr.learn({}, items)
        self.assertEqual(w["w"]["builder"]["rate-limit"], 1)
        w2, changed2 = sr.learn(w, items)
        self.assertEqual(w2["w"]["builder"]["rate-limit"], 1)
        self.assertEqual(changed2, [])

    def test_regression_steps_down_and_unlabeled_is_ignored(self):
        w, _ = sr.learn({}, [{"number": 8, "labels": ["sr:regression", "role:participant"]},
                             {"number": 9, "labels": ["role:builder"]}])
        self.assertEqual(w["w"]["participant"]["self-repair"], -1)
        self.assertNotIn("builder", w["w"])


if __name__ == "__main__":
    unittest.main()
