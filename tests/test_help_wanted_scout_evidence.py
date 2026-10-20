"""Regression tests for evidence-honest Help-Wanted candidate ranking."""
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ci" / "help_wanted_scout.py"
SPEC = importlib.util.spec_from_file_location("help_wanted_scout", MODULE_PATH)
SCOUT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(SCOUT)


class HelpWantedScoutEvidenceTests(unittest.TestCase):
    def candidate(self, **overrides):
        item = {
            "labels": [{"name": "help wanted"}],
            "body": "Expected behavior and acceptance checklist. " + ("Details " * 20),
            "assignees": [],
            "comments": 1,
            "updated_at": "2026-10-18T00:00:00Z",
            "html_url": "https://github.com/example/project/issues/1",
            "title": "Add a documented test",
            "repository_url": "https://api.github.com/repos/example/project",
            "number": 1,
        }
        item.update(overrides)
        return item

    def test_unobserved_signals_are_not_positive_score_components(self):
        result = SCOUT.rank_issue(self.candidate())
        components = result["score_components"]
        self.assertEqual(components["repository_health"], 0)
        self.assertEqual(components["language_fit"], 0)
        self.assertEqual(components["competing_pr_absence"], 0)
        self.assertIn("competing_pr_status_not_checked", result["evidence_gaps"])
        self.assertEqual(result["ranking_status"], "candidate_only")

    def test_score_is_deterministic_for_same_observation_time(self):
        item = self.candidate(updated_at="2026-10-18T00:00:00Z")
        self.assertEqual(SCOUT.rank_issue(item)["score"], SCOUT.rank_issue(item)["score"])

    def test_unknown_language_never_earns_points(self):
        self.assertEqual(SCOUT.language_score("https://github.com/example/project", SCOUT.PREFERRED_LANGS), 0)

    def test_catalog_contract_disclaims_claim_authorization(self):
        # Contract is asserted at the source level to prevent accidental weakening.
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"schema_version": "help-wanted-catalog.v2"', source)
        self.assertIn('"requires_fresh_validation_before_claim": True', source)


if __name__ == "__main__":
    unittest.main()
