"""Tribute System 1 v2: language rule, spam regex, closed_resolved, Drips Wave
assignment, semantic re-engage gate, placeholder-merge weight 0, follow-up cap.

Offline only: every case is a fixture or a synthetic thread built here.
"""
import copy
import json
import unittest
from pathlib import Path

from scripts.ci import tribute_system1 as s1

FX = Path(__file__).resolve().parent / "fixtures" / "tribute_system1"
REAL = {c["case_id"]: c for c in json.loads((FX / "real_backfill_cases.json").read_text(encoding="utf-8"))}
SYN = {c["case_id"]: c for c in json.loads((FX / "synthetic_cases.json").read_text(encoding="utf-8"))}
ME = "timerloggedout-spec"


def comment(cid, author, body, assoc="NONE", at="2026-10-12T10:00:00Z", kind="User"):
    return {"id": cid, "author": author, "author_type": kind, "association": assoc, "created_at": at, "body": body}


def open_pr(comments, reviews=None):
    return {
        "case_id": "v2-synthetic", "synthetic": True, "self_login": ME,
        "subject": {"repo": "acme/widgets", "number": 77, "kind": "pull_request",
                    "url": "https://github.com/acme/widgets/pull/77", "title": "fix parser", "state": "open",
                    "assignees": [], "labels": [], "body": "", "merged": False, "closed_by": None},
        "comments": comments, "reviews": reviews or [],
    }


class SchemaV2(unittest.TestCase):
    def test_schema_and_new_label(self):
        self.assertEqual(s1.SCHEMA, "tribute-system1/v2")
        self.assertIn("closed_resolved", s1.LABELS)
        self.assertEqual(s1.ACTIONS["closed_resolved"], "retire_lane")
        self.assertIn("closed_resolved", s1.NO_REENGAGE)
        self.assertLessEqual(s1.FOLLOWUP_CAP, 2)


class LanguageRule(unittest.TestCase):
    def test_named_language_is_required(self):
        self.assertEqual(s1.skill_requirement("We need a fluent Turkish speaker for this."), "language:turkish")
        self.assertEqual(s1.skill_requirement("must be native in Japanese"), "language:japanese")

    def test_native_build_is_not_a_language_skill(self):
        # codex-termux#14 false positive under v1 ("native build" -> language:unspecified)
        self.assertIsNone(s1.skill_requirement("the native build fails on arm64 with fluent api errors"))

    def test_speakers_without_language_is_unspecified(self):
        self.assertEqual(s1.skill_requirement("this copy needs review by native speakers"), "language:unspecified")

    def test_real_codex_termux_not_flagged(self):
        d = s1.route(REAL["real-dionanos-codex-termux-14"])
        self.assertNotIn("needs_human_skill", {l["label"] for l in d["labels"] if l["confidence"] >= s1.CONFIDENT})


class SpamRegex(unittest.TestCase):
    def test_reported_alone_is_not_spam(self):
        self.assertIsNone(s1.RX["spam"].search("I reported this bug upstream last week."))

    def test_ban_request_is_confident(self):
        self.assertTrue(s1.RX["spam"].search("can you repoban that bot please"))
        self.assertTrue(s1.RX["ban_request"].search("can you repoban that bot please"))
        d = s1.route(REAL["real-deltav-station-delta-v-6533"])
        self.assertEqual(d["primary"], "hostile_spam_flag")
        spam = [l for l in d["labels"] if l["label"] == "hostile_spam_flag"][0]
        self.assertGreaterEqual(spam["confidence"], s1.CONFIDENT)
        self.assertIn("repo_cooldown", {r["rule"] for r in d["prefilter_rules"]})

    def test_old_false_positives_cleared(self):
        for cid in ("real-glasshaven-haven-273", "real-pyrite-wiki-pyrite-192"):
            d = s1.route(REAL[cid])
            self.assertNotEqual(d["primary"], "hostile_spam_flag", cid)
            self.assertIsNone(d["owner_required"], cid)


class ClosedResolved(unittest.TestCase):
    def test_closed_by_merge(self):
        d = s1.route(REAL["real-gritui-pixel-builder-11"])
        self.assertEqual((d["primary"], d["action"]), ("closed_resolved", "retire_lane"))
        self.assertFalse(d["reengage_allowed"])
        self.assertIn("require_open_issue", {r["rule"] for r in d["prefilter_rules"]})
        self.assertLess(d["delphi_signal"]["weight"], 0)

    def test_claimed_after_close(self):
        d = s1.route(REAL["real-glasshaven-haven-273"])
        self.assertEqual(d["primary"], "closed_resolved")
        self.assertTrue(d["features"]["claimed_after_close"])


class DripsWave(unittest.TestCase):
    def test_wave_accepted_yields(self):
        d = s1.route(REAL["real-labscrypt-remitlend-1503"])
        self.assertEqual((d["primary"], d["action"]), ("claimed_by_other", "yield_lane"))
        self.assertTrue(d["features"]["wave_accepted"])
        self.assertIn("skip_bounty_program_issue", {r["rule"] for r in d["prefilter_rules"]})

    def test_wave_completed_closed_retires(self):
        d = s1.route(REAL["real-apexchainx-apexchainx-contracts-659"])
        self.assertEqual((d["primary"], d["action"]), ("closed_already_assigned", "retire_lane"))
        self.assertTrue(d["features"]["wave_completed"])

    def test_preflight_refuses_wave_issue(self):
        issue = {"repo": "o/r", "number": 1, "state": "open", "assignees": [], "body": "fix it"}
        cm = [comment(1, "wave-bot", "Congratulations, @someone! Your application was accepted for this issue.")]
        pf = s1.preflight_candidate(issue, cm)
        self.assertFalse(pf["eligible"])
        self.assertTrue(any(r.startswith("wave_accepted:someone") for r in pf["reasons"]))

    def test_preflight_eligible_clean_issue(self):
        issue = {"repo": "o/r", "number": 2, "state": "open", "assignees": [], "body": "Typo in README"}
        self.assertTrue(s1.preflight_candidate(issue, [])["eligible"])


class SemanticReengageGate(unittest.TestCase):
    def test_semantic_decline_blocks_followup(self):
        # No decline keyword hits, but semantically "someone else already works on this".
        t = open_pr([comment(1, "acme", "@timerloggedout-spec thanks, please add tests before we can merge.", "OWNER",
                             at="2026-10-10T10:00:00Z"),
                     comment(2, "passerby", "someone else already claimed this one and is working on it", "NONE",
                             at="2026-10-11T10:00:00Z")])
        d = s1.route(t)
        self.assertFalse(d["reengage_allowed"])
        self.assertIn(d["reengage_block"], ("semantic_decline", "class"))

    def test_clean_changes_request_still_reengages(self):
        d = s1.route(SYN["syn-changes"])
        self.assertTrue(d["reengage_allowed"])
        self.assertIsNone(d["reengage_block"])

    def test_issue_threads_never_reengage(self):
        d = s1.route(SYN["syn-quiet"])
        self.assertFalse(d["reengage_allowed"])

    def test_semantic_scores_are_deterministic(self):
        a = s1.semantic_scores("closing this because the issue is already assigned to another contributor")
        b = s1.semantic_scores("closing this because the issue is already assigned to another contributor")
        self.assertEqual(a, b)
        self.assertEqual(max(a, key=a.get), "closed_already_assigned")


class PlaceholderMerge(unittest.TestCase):
    def test_placeholder_merge_weight_zero(self):
        for cid in ("real-gritui-pixel-builder-13", "real-nodal-stellar-nodal-ai-853"):
            d = s1.route(REAL[cid])
            self.assertEqual(d["primary"], "merged", cid)
            self.assertEqual(d["action"], "record_placeholder_merge", cid)
            self.assertEqual(d["delphi_signal"]["weight"], 0.0, cid)
            self.assertEqual(d["delphi_signal"]["lesson"], "placeholder_merge_not_a_win")

    def test_real_merge_keeps_full_weight(self):
        d = s1.route(SYN["syn-merged"])
        self.assertEqual(d["delphi_signal"]["weight"], 1.0)

    def test_preflight_pr_refuses_stake_file(self):
        self.assertFalse(s1.preflight_pr([{"filename": ".github/help-wanted-lane-stake.md", "additions": 8}])["allowed"])
        self.assertTrue(s1.preflight_pr([{"filename": "src/parser.py", "additions": 30, "patch": "+def parse(x):\n+    return x.strip()"}])["allowed"])


class FollowupCap(unittest.TestCase):
    def base(self, n_self):
        cms = [comment(1, "acme", "@timerloggedout-spec Please add a unit test and rebase on main.", "OWNER",
                       at="2026-10-10T10:00:00Z")]
        for i in range(n_self):
            cms.append(comment(10 + i, ME, "Friendly follow-up: updated per review.", "NONE", at=f"2026-10-1{1 + i}T10:00:00Z"))
        return open_pr(cms, reviews=[{"state": "CHANGES_REQUESTED"}])

    def test_one_unanswered_followup_allowed(self):
        d = s1.route(self.base(1))
        self.assertEqual(d["features"]["self_tail_comments"], 1)
        self.assertTrue(d["reengage_allowed"])

    def test_cap_reached_blocks(self):
        for n in (2, 3, 6):
            d = s1.route(self.base(n))
            self.assertFalse(d["reengage_allowed"], n)
            self.assertEqual(d["reengage_block"], "followup_cap", n)
            self.assertIn("followup_cap", {r["rule"] for r in d["prefilter_rules"]})

    def test_real_sendam_six_nudges_blocked(self):
        d = s1.route(REAL["real-ef-chain-sendam-492"])
        self.assertFalse(d["reengage_allowed"])


class RealBackfillFixtures(unittest.TestCase):
    def test_all_real_cases_match(self):
        bad = []
        for cid, c in REAL.items():
            d = s1.route(c)
            exp = c["expected"]
            if (d["primary"], d["action"]) != (exp["primary"], exp["action"]) or d["reengage_allowed"] != exp["reengage_allowed"]:
                bad.append((cid, d["primary"], d["action"]))
            self.assertIsNone(d["owner_required"], cid)  # no HITL rung
        self.assertEqual(bad, [])

    def test_no_case_mutated_by_routing(self):
        c = REAL["real-gritui-pixel-builder-13"]
        before = copy.deepcopy(c)
        s1.route(c)
        self.assertEqual(c, before)


if __name__ == "__main__":
    unittest.main()
