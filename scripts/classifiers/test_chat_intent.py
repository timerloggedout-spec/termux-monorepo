"""Tests for chat-intent v2 (rules tier; v1 regression set kept)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chat_intent import classify  # noqa: E402


class ChatIntent(unittest.TestCase):
    def test_motivating_miss_is_request(self):
        # 2026-11-01: read as speculation by main; owner corrected.
        r = classify("DoE likely it's own AppID && Repo etc")
        self.assertEqual(r["intent"], "request")
        self.assertEqual(r["rule"], "R4-hedge+artifact")

    def test_question(self):
        r = classify("BTW how's the Tier 1 Classifiers Lane?")
        self.assertEqual(r["intent"], "question")

    def test_directive(self):
        r = classify("Add a side chat here to follow it & Steward.")
        self.assertEqual(r["intent"], "directive")

    def test_speculation(self):
        r = classify("Maybe someday the whole fleet gets cheaper "
                     "and things just work out")
        self.assertEqual(r["intent"], "speculation")

    def test_aside(self):
        r = classify("nice, thanks — good landing")
        self.assertEqual(r["intent"], "aside")

    def test_ability_form_is_request(self):
        r = classify("can you check the pr-lane feed?")
        self.assertEqual(r["intent"], "request")

    def test_evidence_carried(self):
        r = classify("DoE likely it's own AppID && Repo etc")
        self.assertIn("likely", r["hedges"])
        self.assertTrue({"appid", "repo"} <= set(r["artifacts"]))


class ChatIntentV2Do(unittest.TestCase):
    """v2: DO Statements (owner ruling 2026-11-02)."""

    def test_do_adjective_stack(self):
        r = classify("Resilient Efficient Effective")
        self.assertEqual(r["intent"], "do")
        self.assertEqual(r["rule"], "R6-do-statement")

    def test_do_alliterative_maxim(self):
        r = classify("Proper Prior Planning")
        self.assertEqual(r["intent"], "do")

    def test_do_standing_kin(self):
        r = classify("alternatives are priority")
        self.assertEqual(r["intent"], "do")
        self.assertTrue({"alternatives", "priority"} <= set(r["do_lexicon"]))

    def test_maxim_with_artifact_action_stays_request(self):
        # R5 fires before R6: an actionable maxim is a request.
        r = classify("always build the repo first")
        self.assertEqual(r["intent"], "request")

    def test_hedged_principle_stays_speculation(self):
        r = classify("maybe quality someday wins out somehow")
        self.assertEqual(r["intent"], "speculation")


if __name__ == "__main__":
    unittest.main()
