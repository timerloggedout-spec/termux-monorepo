"""Tribute System 1: seed cases, ladder, preflight, Gmail fallback, eval gate."""
import json
import unittest
from pathlib import Path

from scripts.ci import tribute_system1 as s1
from scripts.ci import tribute_system1_eval as ev

FX = Path(__file__).resolve().parent / "fixtures" / "tribute_system1"


def load(name):
    return json.loads((FX / name).read_text(encoding="utf-8"))


class SeedCases(unittest.TestCase):
    def check(self, name):
        case = load(name)
        d = s1.route(case)
        exp = case["expected"]
        self.assertEqual(d["primary"], exp["primary"])
        self.assertEqual(d["action"], exp["action"])
        self.assertFalse(d["escalate"])
        self.assertFalse(d["reengage_allowed"])
        confident = {l["label"] for l in d["labels"] if l["confidence"] >= s1.CONFIDENT}
        self.assertTrue(set(exp["labels"]) <= confident, (exp["labels"], d["labels"]))
        rules = {r["rule"] for r in d["prefilter_rules"]}
        self.assertTrue(set(exp["prefilter_rules"]) <= rules, rules)
        return d

    def test_seed1_resqnet_closed_assigned_placeholder(self):
        d = self.check("seed1_resqnet_pr53.json")
        self.assertTrue(d["features"]["placeholder"]["is_placeholder"])
        self.assertIn("nishu91020", d["features"]["assigned_to_other"])
        self.assertLess(d["delphi_signal"]["weight"], 0)

    def test_seed2_kdemos_needs_turkish(self):
        d = self.check("seed2_kdemos_issue26.json")
        self.assertEqual(d["features"]["skill"], "language:turkish")

    def test_seed3_selenium_claimed_by_other(self):
        d = self.check("seed3_selenium_boot_issue180.json")
        self.assertEqual(d["features"]["claims_before_us"][0]["author"], "aryantawade123-sys")
        spam = [l for l in d["labels"] if l["label"] == "hostile_spam_flag"]
        self.assertTrue(spam and spam[0]["confidence"] < s1.CONFIDENT)  # contributor remark, informational


class Ladder(unittest.TestCase):
    def setUp(self):
        self.cases = {c["case_id"]: c for c in load("synthetic_cases.json")}

    def test_low_confidence_goes_to_llm_then_replans_when_unsure(self):
        c = self.cases["syn-ambiguous"]
        self.assertEqual(s1.route(c)["rung"], "system2_llm")
        d = s1.route(c, system2={"label": "question_to_us", "confidence": 0.4, "unsure": True})
        self.assertEqual(d["rung"], "replan")
        self.assertEqual(d["action"], "park_lane")
        self.assertIn("pick_next_candidate", d["plan"]["steps"])
        self.assertIsNone(d["owner_required"])
        self.assertNotIn("hark_queue", d)
        self.assertNotIn("hitl", d)
        self.assertEqual(d["audit"]["state"], "RECORDED")

    def test_unsure_llm_on_claimed_thread_replans_to_yield(self):
        d = s1.route(load("seed3_selenium_boot_issue180.json"), labels=[], system2={"unsure": True})
        self.assertEqual(d["plan"]["steps"][0], "yield_lane")

    def test_confident_llm_verdict_routes_without_human(self):
        d = s1.route(self.cases["syn-ambiguous"], system2={"label": "needs_human_skill", "confidence": 0.9})
        self.assertEqual((d["rung"], d["action"]), ("system2_llm", "drop_candidate"))
        self.assertIsNone(d["owner_required"])

    def test_public_reply_is_the_only_owner_stop(self):
        d = s1.route(self.cases["syn-question"], system2={"label": "question_to_us", "confidence": 0.9, "needs_public_reply": True})
        self.assertEqual(d["owner_required"], "post_on_third_party_repo")
        self.assertEqual(d["action"], "park_lane")

    def test_question_to_us_goes_to_llm_not_a_person(self):
        d = s1.route(self.cases["syn-question"])
        self.assertEqual(d["rung"], "system2_llm")
        self.assertFalse(d["reengage_allowed"])

    def test_maintainer_spam_retires_without_human(self):
        d = s1.route(self.cases["syn-spam"])
        self.assertEqual(d["action"], "retire_lane_cooldown")
        self.assertFalse(d["escalate"])

    def test_reengage_gate(self):
        self.assertTrue(s1.reengage_allowed(self.cases["syn-changes"]))
        for name in ("seed1_resqnet_pr53.json", "seed2_kdemos_issue26.json", "seed3_selenium_boot_issue180.json"):
            self.assertFalse(s1.reengage_allowed(load(name)), name)

    def test_lane_event_shape_matches_lane_event_py(self):
        ev_ = s1.route(load("seed2_kdemos_issue26.json"))["lane_event"]
        for k in ("lane", "workflow", "event_type", "repo", "subject_url"):
            self.assertTrue(ev_[k], k)


class Preflight(unittest.TestCase):
    def test_issue50_assigned_is_ineligible(self):
        li = load("seed1_resqnet_pr53.json")["linked_issue"]
        r = s1.preflight_candidate(li, li["comments"])
        self.assertFalse(r["eligible"])
        self.assertTrue(any(x.startswith("assigned:") for x in r["reasons"]))

    def test_kdemos_language_filter_from_issue_body(self):
        s = load("seed2_kdemos_issue26.json")["subject"]
        r = s1.preflight_candidate(s, [])  # body alone: "You need to speak Turkish"
        self.assertIn("needs_human_skill:language:turkish", r["reasons"])

    def test_selenium_prior_claim_curly_apostrophe(self):
        c = load("seed3_selenium_boot_issue180.json")
        r = s1.preflight_candidate(c["subject"], c["comments"][:1])
        self.assertIn("claimed_by:aryantawade123-sys", r["reasons"])

    def test_clean_issue_is_eligible(self):
        self.assertTrue(s1.preflight_candidate({"state": "open", "assignees": [], "body": "Fix the typo in README."}, [])["eligible"])

    def test_stake_only_pr_is_blocked(self):
        files = load("seed1_resqnet_pr53.json")["files"]
        self.assertFalse(s1.preflight_pr(files)["allowed"])
        self.assertTrue(s1.preflight_pr([{"filename": "src/app.ts", "additions": 40, "deletions": 3, "patch": "+const x = 1"}])["allowed"])


class Ingest(unittest.TestCase):
    def test_dedupe_by_comment_id(self):
        cs = [{"id": 1, "body": "a"}, {"id": 1, "body": "a"}, {"id": 2, "body": "b"}]
        seen = {"2"}
        self.assertEqual([c["id"] for c in s1.dedupe_comments(cs, seen)], [1])

    def test_gmail_notification_fallback(self):
        body = ("@timerloggedout-spec this issue needs a fluent Turkish speaker (it's marketing copy, not a code change), "
                "so I'm not assigning it to an automated lane.\n\n—\nReply to this email directly, view it on GitHub:\n"
                "https://github.com/francordel/kdemos/issues/26#issuecomment-6301404363\n")
        t = s1.parse_github_email("Re: [francordel/kdemos] Add the Turkish landing page (/tr/) for SEO (Issue #26)", body,
                                  "francordel <notifications@github.com>")
        self.assertEqual(t["comments"][0]["id"], "6301404363")
        d = s1.route(t)
        self.assertEqual(d["primary"], "needs_human_skill")
        self.assertFalse(d["reengage_allowed"])

    def test_no_writes_in_module(self):
        src = (Path(s1.__file__)).read_text(encoding="utf-8")
        for verb in ('method="POST"', "method='POST'", '"PATCH"', '"PUT"', '"DELETE"'):
            self.assertNotIn(verb, src)


class EvalGate(unittest.TestCase):
    def test_eval_passes_and_has_zero_false_reengage(self):
        r = ev.evaluate(ev.load_cases([FX]))
        self.assertEqual(r["false_reengage"], [])
        self.assertEqual(r["hitl_rate"], 0.0)
        self.assertLessEqual(r["llm_call_rate"], 0.35)
        self.assertEqual(r["seed_failures"], [])
        self.assertGreaterEqual(r["macro_precision"], 0.9)
        self.assertGreaterEqual(r["macro_recall"], 0.9)


if __name__ == "__main__":
    unittest.main()
