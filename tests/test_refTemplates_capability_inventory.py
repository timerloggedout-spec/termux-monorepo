"""Tests for category-aware refTemplates metadata inventory and scoring."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ci.refTemplates_inventory import capability_child_entry, inventory_entry, REF
from scripts.ci.refTemplates_score import score_capability_child, score_child, validate_rows


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

    def test_file_based_markdown_references_are_inventory_candidates(self):
        expected = {
            "boinc-distributed-compute-template",
            "context-retrieval-architect",
            "done-gate",
            "neo4j-relate",
        }
        with tempfile.TemporaryDirectory(dir=REF) as temp:
            slot = Path(temp) / "13_Third_Party_Refs"
            slot.mkdir()
            (slot / "README.md").write_text("# Category index\n", encoding="utf-8")
            (slot / "SOURCE-MAP.md").write_text("# Source map\n", encoding="utf-8")
            (slot / "boinc-distributed-compute-template.md").write_text(
                "# BOINC\n\nOwner ruling: fleet template pattern.\n", encoding="utf-8"
            )
            (slot / "context-retrieval-architect.md").write_text(
                "# Context retrieval\n\n- Pattern source: Box Architect (2026-11-08).\n",
                encoding="utf-8",
            )
            (slot / "done-gate.md").write_text(
                "# Done Gate\n\n- Concept source: Codenotary AgentMon Live.\n",
                encoding="utf-8",
            )
            (slot / "neo4j-relate.md").write_text(
                "# Neo4j Relate\n\n- Source: https://example.org/release.\n",
                encoding="utf-8",
            )
            row = inventory_entry(slot)

        self.assertEqual(4, row["candidate_count"])
        self.assertEqual(expected, {child["name"] for child in row["candidate_children"]})
        self.assertTrue(all(child["file_reference"] for child in row["candidate_children"]))
        self.assertTrue(all(child["has_reference_document"] for child in row["candidate_children"]))
        by_name = {child["name"]: child for child in row["candidate_children"]}
        self.assertEqual("source_recorded", by_name["context-retrieval-architect"]["provenance_state"])
        self.assertEqual("metadata_only", by_name["boinc-distributed-compute-template"]["provenance_state"])

    def test_file_reference_scores_documentation_and_source_attribution(self):
        score = score_capability_child({
            "name": "context-retrieval-architect",
            "category": "13_Third_Party_Refs",
            "path": "refTemplates/13_Third_Party_Refs/context-retrieval-architect.md",
            "has_source": True,
            "has_readme": False,
            "has_reference_document": True,
            "file_reference": True,
            "metadata_files": ["context-retrieval-architect.md"],
            "source_preview": "Pattern source: Box Architect (2026-11-08)",
            "provenance_state": "source_recorded",
        })
        self.assertEqual(0.8, score["readiness_score"])
        self.assertTrue(score["file_reference"])
        self.assertTrue(score["has_reference_document"])

    def test_empty_source_file_keeps_attribution_and_pin_credit_unearned(self):
        sha = "b" * 40
        with tempfile.TemporaryDirectory(dir=REF) as temp:
            slot = Path(temp) / "11_Evaluation_Quality"
            child = slot / "empty-source"
            child.mkdir(parents=True)
            (child / "README.md").write_text("# Empty source candidate\n", encoding="utf-8")
            (child / "SOURCE.txt").write_text("  \n", encoding="utf-8")
            (child / "metadata.yaml").write_text(
                f"source: https://github.com/org/repo/tree/{sha}\n", encoding="utf-8"
            )
            row = inventory_entry(slot)
        candidate = row["candidate_children"][0]
        score = score_capability_child(candidate)
        self.assertFalse(candidate["has_source"])
        self.assertEqual("metadata_only", candidate["provenance_state"])
        self.assertEqual(0.0, score["layers"]["source_attribution"])
        self.assertEqual(0.0, score["layers"]["revision_specificity"])

    def test_revision_pin_requires_complete_immutable_revision(self):
        def specificity(preview: str) -> float:
            return score_capability_child({
                "name": "pin-case",
                "category": "13_Third_Party_Refs",
                "has_source": True,
                "has_reference_document": True,
                "metadata_files": ["reference.md"],
                "source_preview": preview,
            })["layers"]["revision_specificity"]

        sha = "a" * 40
        self.assertEqual(0.0, specificity("https://github.com/org/repo/tree/v1"))
        self.assertEqual(0.0, specificity("https://github.com/org/repo/tree/v1.2"))
        self.assertEqual(0.0, specificity("https://github.com/org/repo/tree/v1.2.3"))
        self.assertEqual(0.0, specificity("https://github.com/org/repo/tree/v2-experimental"))
        self.assertEqual(0.0, specificity("https://github.com/org/repo/tree/2026-11-experiment"))
        self.assertEqual(1.0, specificity("https://github.com/org/repo/releases/tag/v1.2.3"))
        self.assertEqual(1.0, specificity(f"https://github.com/org/repo/tree/{sha}"))
        self.assertEqual(1.0, specificity(f"https://github.com/org/repo/commit/{sha}"))

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

    def test_score_contract_rejects_efficacy_claims_without_runs(self):
        row = score_capability_child({
            "name": "assert",
            "category": "11_Evaluation_Quality",
            "path": "refTemplates/11_Evaluation_Quality/assert",
            "has_source": True,
            "has_readme": True,
            "metadata_files": ["SOURCE.txt"],
            "source_preview": "https://github.com/responsibleai/ASSERT",
            "provenance_state": "source_recorded",
        })
        row["efficacy_score"] = 0.99
        self.assertTrue(any("efficacy must remain unmeasured" in error for error in validate_rows([row])))

    def test_research_template_profile_remains_distinct(self):
        score = score_child("jogyo-research-lab", True, True, "https://github.com/Yeachan-Heo/My-Jogyo")
        self.assertEqual("research_template", score["candidate_class"])
        self.assertEqual("B", score["tier"])


if __name__ == "__main__":
    unittest.main()
