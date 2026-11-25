"""Tests for category-aware refTemplates metadata inventory and scoring."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ci.refTemplates_inventory import capability_child_entry, inventory_entry, REF
from scripts.ci.refTemplates_score import score_capability_child, score_child


class RefTemplatesCapabilityInventoryTests(unittest.TestCase):
    def test_source_and_readme_create_attributed_candidate(self):
        with tempfile.TemporaryDirectory(dir=REF) as temp:
            slot = Path(temp) / "11_Evaluation_Quality"
            child = slot / "assert"
            child.mkdir(parents=True)
            (child / "README.md").write_text("# ASSERT\n", encoding="utf-8")
            (child / "SOURCE.txt").write_text("https://github.com/responsibleai/ASSERT\n", encoding="utf-8")
            row = capability_child_entry(slot, child)
        self.assertEqual("source_recorded", row["provenance_state"])
        self.assertTrue(row["has_source"])
        self.assertTrue(row["has_readme"])
        self.assertEqual("https://github.com/responsibleai/ASSERT", row["source_preview"])

    def test_metadata_only_candidate_stays_unattributed_to_upstream(self):
        with tempfile.TemporaryDirectory(dir=REF) as temp:
            slot = Path(temp) / "07_Prompt_Context"
            child = slot / "candidate"
            child.mkdir(parents=True)
            (child / "README.md").write_text("# Candidate\n", encoding="utf-8")
            row = capability_child_entry(slot, child)
        self.assertEqual("metadata_only", row["provenance_state"])
        self.assertFalse(row["has_source"])

    def test_inventory_emits_category_candidates_separately_from_research(self):
        with tempfile.TemporaryDirectory(dir=REF) as temp:
            slot = Path(temp) / "05_Safety_Observability"
            child = slot / "candidate"
            child.mkdir(parents=True)
            (child / "README.md").write_text("# Candidate\n", encoding="utf-8")
            row = inventory_entry(slot)
        self.assertEqual(1, row["candidate_count"])
        self.assertEqual([], row["research_children"])
        self.assertEqual("05_Safety_Observability", row["candidate_children"][0]["category"])

    def test_capability_score_measures_metadata_readiness_only(self):
        score = score_capability_child({
            "name": "assert",
            "category": "11_Evaluation_Quality",
            "path": "refTemplates/11_Evaluation_Quality/assert",
            "has_source": True,
            "has_readme": True,
            "metadata_files": ["SOURCE.txt"],
            "source_preview": "https://github.com/responsibleai/ASSERT",
            "provenance_state": "source_recorded",
        })
        self.assertEqual("capability_reference", score["candidate_class"])
        self.assertEqual("metadata_readiness_only", score["score_scope"])
        self.assertIsNone(score["efficacy_score"])
        self.assertEqual("unmeasured", score["validation_state"])
        self.assertEqual("metadata_candidate", score["readiness_band"])

    def test_research_template_profile_remains_distinct(self):
        score = score_child("jogyo-research-lab", True, True, "https://github.com/Yeachan-Heo/My-Jogyo")
        self.assertEqual("research_template", score["candidate_class"])
        self.assertEqual("A", score["tier"])


if __name__ == "__main__":
    unittest.main()
