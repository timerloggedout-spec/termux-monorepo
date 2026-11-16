"""Tests for the notation compliance scorer (heuristic v1 + v2)."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compliance_scorer import (adjacency, connective_symbols, features,  # noqa: E402
                               load_operator_set, score, score_v2)

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


OPS = {"→", "⇒", "∧", "∨", "¬", "∴", "∵", "←", "✓"}
PAN_STYLE = ("A category consists of objects and morphisms. Morphism "
             "assignment: f: A → B means f is an arrow with domain A. "
             "Composition: g ∘ f : A → C, read as g after f [1, 2]. "
             "The identity arrow id_A maps each object to itself, and "
             "functors preserve this structure between categories.")
SKELETON = ('{"provider": "g4f", "evidence": "not-established", '
            '"free_tier": {"state": "not-established"}, '
            '"credits": {"available": "not-established", "balance": null}, '
            '"verdict": "not-established", "flags": []}')
DECORATIVE = ("See also the related material collected elsewhere: "
              "#111 #222 #333 #444 and the archive at "
              "https://example.com/a https://example.com/b plus "
              "notes in docs/x.md docs/y.md docs/z.md for background.")


class V2Features(unittest.TestCase):
    def test_adjacency_counts_claim_refs(self):
        a = adjacency(DENSE)
        self.assertGreaterEqual(a["adj_refs"], 3)

    def test_decorative_refs_not_adjacent(self):
        a = adjacency(DECORATIVE)
        self.assertEqual(a["adj_refs"], 0)
        self.assertGreater(a["refs_total"], 5)

    def test_symbol_function_connective_vs_listed(self):
        c = connective_symbols("A ∧ B ⇒ C ∴ D", OPS)
        self.assertEqual(c["connective_sym"], 3)
        listed = connective_symbols("symbols: ∧ ∨ ¬ are listed", OPS)
        self.assertEqual(listed["connective_sym"], 0)

    def test_pan_style_not_drift_under_v2(self):
        r = score_v2(PAN_STYLE, OPS)
        self.assertNotEqual(r["verdict_v2"], "prose")

    def test_records_skeleton_is_drift_under_v2(self):
        r = score_v2(SKELETON, OPS)
        self.assertEqual(r["verdict_v2"], "prose")
        self.assertEqual(r["adj_refs"], 0)

    def test_dense_stays_compliant_under_v2(self):
        r = score_v2(DENSE, OPS)
        self.assertEqual(r["verdict_v2"], "compliant")

    def test_operator_set_is_registry_derived(self):
        feed = {"families": [{"id": "f1", "kind_detail": "symbol-map"},
                             {"id": "f2", "kind_detail": "word-map"}],
                "entries": [
                    {"family_id": "f1", "variants": "['→', '∧']"},
                    {"family_id": "f2", "variants": "['≫']"}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(feed, fh)
            path = fh.name
        ops = load_operator_set(path)
        self.assertEqual(ops, {"→", "∧"})  # word-map family excluded;
        # a glyph absent from the registry is absent from the set —
        # the set comes from the feed, never from a hard-coded list.
        self.assertNotIn("≫", ops)


if __name__ == "__main__":
    unittest.main()
