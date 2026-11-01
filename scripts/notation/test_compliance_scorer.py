"""Tests for the notation compliance scorer (heuristic v1)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compliance_scorer import features, score  # noqa: E402

DENSE = ("[MUSEai]@{role:{tier1-classifiers-steward}} ENROLL ↦ filed. "
         "Slice ∅ firsthand: plan blob 691c44a88435 ∧ allocations bc9a325521b8 "
         "⇒ hits = 0 ⇒ filed #1884 comment 6520942443, ¬ self-assigned. "
         "Timers ✓ per QAC-008: cron `37 5 * * *` + dispatch, ≈210 calls/run.")
PROSE = ("I wanted to provide a comprehensive update regarding the current "
         "status of the project, because several important developments have "
         "taken place recently. However, it is worth noting that the overall "
         "situation remains somewhat uncertain, and therefore we should "
         "carefully consider the various options that are available to us "
         "before making any final decisions about how to proceed.")


class Scorer(unittest.TestCase):
    def test_dense_is_compliant(self):
        r = score(DENSE)
        self.assertEqual(r["verdict"], "compliant")
        self.assertGreater(r["sym_per_100w"], 3.0)
        self.assertGreater(r["ev_per_100w"], 2.0)

    def test_prose_is_prose(self):
        r = score(PROSE)
        self.assertEqual(r["verdict"], "prose")
        self.assertGreater(r["glue_per_sent"], 1.0)
        self.assertGreater(r["mean_sent_words"], 20)

    def test_empty_does_not_crash(self):
        r = score("")
        self.assertEqual(r["words"], 0)
        self.assertIn(r["verdict"], ("compliant", "borderline", "prose"))

    def test_features_normalized(self):
        f = features(DENSE + " " + DENSE)
        self.assertAlmostEqual(f["sym_per_100w"], features(DENSE)["sym_per_100w"], places=1)


if __name__ == "__main__":
    unittest.main()
