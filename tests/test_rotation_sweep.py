from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.identity.rotation_sweep import (
    classify_line, check_identity_registry, score_fixtures, validate_mapping, scan_repository,
)


class RotationSweepTests(unittest.TestCase):
    def setUp(self):
        self.rotation_map = {
            "entries": [
                {"source": "AGENTS.md", "target": "CLAUDE.md"},
                {"source": "GEMINI.md", "target": "GEMINI-MESH.md"},
                {"source": "docs/ops/AGENT-MONIKERS.md",
                 "target": "docs/ops/COLLABORATOR-MONIKERS.md"},
                {"source": "docs/ops/AGENT-IDENTITY.md",
                 "target": "docs/ops/COLLABORATOR-IDENTITY.md"},
            ]
        }

    def test_independent_classifier_families_detect_distinct_signals(self):
        workflow = classify_line(
            ".github/workflows/review.yml",
            "Read GEMINI.md before dispatch",
            self.rotation_map["entries"],
        )
        self.assertTrue(workflow["lexical"])
        self.assertTrue(workflow["workflow"])
        self.assertTrue(workflow["semantic"])

        link = classify_line(
            "docs/guide.md",
            "[Roster](docs/ops/AGENT-MONIKERS.md)",
            self.rotation_map["entries"],
        )
        self.assertTrue(link["link"])
        self.assertTrue(link["lexical"])

    def test_semantic_classifier_separates_historical_and_tool_only_text(self):
        historical = classify_line(
            "docs/history.md",
            "GEMINI.md was renamed during the migration",
            self.rotation_map["entries"],
        )
        self.assertEqual(historical["context"], "historical")
        self.assertFalse(historical["semantic"])

        tool = classify_line(
            ".github/workflows/gemini.yml",
            "uses: google-github-actions/run-gemini-cli@v1",
            self.rotation_map["entries"],
        )
        self.assertFalse(tool["lexical"])
        self.assertFalse(tool["workflow"])

    def test_full_factorial_has_all_classifier_combinations(self):
        result = score_fixtures(self.rotation_map)
        self.assertEqual(result["design"], "full_factorial_2^5")
        self.assertEqual(result["fixture_count"], 8)
        self.assertEqual(len(result["arms"]), 32)
        self.assertTrue(all(0.0 <= arm["accuracy"] <= 1.0
                            for arm in result["arms"]))

    def test_mapping_requires_targets_and_retired_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CLAUDE.md").write_text("governance")
            (root / "GEMINI-MESH.md").write_text("profile")
            (root / "docs/ops").mkdir(parents=True)
            (root / "docs/ops/COLLABORATOR-MONIKERS.md").write_text("roster")
            (root / "docs/ops/COLLABORATOR-IDENTITY.md").write_text("identity")
            errors = validate_mapping(root, self.rotation_map)
            self.assertEqual(errors, [])

            (root / "GEMINI.md").write_text("legacy")
            errors = validate_mapping(root, self.rotation_map)
            self.assertTrue(any("legacy source path remains" in item
                                for item in errors))

    def test_identity_registry_detects_duplicate_monikers_and_trigger_collisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "COLLABORATOR-MONIKERS.md"
            path.write_text(
                "| Role | Display moniker | Live trigger | Notes |\n"
                "|---|---|---|---|\n"
                "| A | `sameName` | @other | |\n"
                "| B | `sameName` | @sameName | |\n",
                encoding="utf-8",
            )
            result = check_identity_registry(path)
            self.assertEqual(result["duplicate_monikers"], ["samename"])
            self.assertEqual(result["trigger_collisions"], ["sameName"])
            self.assertFalse(result["passed"])


    def test_named_profile_is_loaded_and_audited_by_every_gemini_route(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            ".github/workflows/gemini-review.yml",
            ".github/workflows/gemini-after-peers.yml",
            ".github/workflows/gemini-invoke.yml",
            ".github/workflows/gemini-triage.yml",
        ):
            self.assertIn("GEMINI-MESH.md", (root / rel).read_text(encoding="utf-8"), rel)
        ecc = (root / ".github/workflows/agent-ecc-tools-ops.yml").read_text(encoding="utf-8")
        self.assertIn("**/GEMINI-MESH.md", ecc)
        self.assertIn("GEMINI-MESH\\.md$", ecc)
        maintenance = root / "docs/icm/maintenance/ICM-MAP-MAINTENANCE.md"
        self.assertTrue(maintenance.is_file())
        self.assertFalse((root / "docs/icm/maintenance/AGENTS.md").exists())


    def test_historical_allowlist_preserves_provenance_without_active_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "archive"
            archive.mkdir()
            (archive / "record.md").write_text(
                "The old AGENTS.md reference is historical evidence.",
                encoding="utf-8",
            )
            rotation_map = {
                "entries": [{"source": "AGENTS.md", "target": "CLAUDE.md"}],
                "historical_reference_paths": ["archive/record.md"],
            }
            report = scan_repository(root, rotation_map)
            self.assertEqual(len(report["historical_refs"]), 1)
            self.assertEqual(report["active_refs"], [])
            self.assertEqual(report["ambiguous_refs"], [])


if __name__ == "__main__":
    unittest.main()
