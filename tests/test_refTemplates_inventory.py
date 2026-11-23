import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ci import refTemplates_inventory as inventory


class RefTemplatesInventoryTests(unittest.TestCase):
    def test_tier_c_pattern_child_requires_readme_and_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            slot = root / "13_Third_Party_Refs"
            child = slot / "spaceship-ide"
            child.mkdir(parents=True)
            (child / "README.md").write_text("# Spaceship IDE\n", encoding="utf-8")
            (child / "SOURCE.txt").write_text(
                "Preferred SOURCE: https://example.test/repo\n", encoding="utf-8"
            )

            with patch.object(inventory, "ROOT", root):
                entry = inventory.inventory_entry(slot)

            self.assertEqual(
                entry["pattern_children"],
                [
                    {
                        "name": "spaceship-ide",
                        "has_source": True,
                        "has_readme": True,
                        "source_preview": "Preferred SOURCE: https://example.test/repo",
                    }
                ],
            )
            self.assertEqual(inventory.validate([entry]), [])

    def test_tier_c_pattern_child_reports_each_missing_metadata_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            slot = root / "13_Third_Party_Refs"
            (slot / "spaceship-ide").mkdir(parents=True)

            with patch.object(inventory, "ROOT", root):
                entry = inventory.inventory_entry(slot)

            self.assertEqual(
                inventory.validate([entry]),
                [
                    "13_Third_Party_Refs/spaceship-ide: missing SOURCE.txt",
                    "13_Third_Party_Refs/spaceship-ide: missing README.md",
                ],
            )

    def test_whitespace_only_source_has_null_preview_and_preserves_presence_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            slot = root / "13_Third_Party_Refs"
            child = slot / "spaceship-ide"
            child.mkdir(parents=True)
            (child / "README.md").write_text("# Spaceship IDE\n", encoding="utf-8")
            (child / "SOURCE.txt").write_text("\n  \t\n", encoding="utf-8")

            with patch.object(inventory, "ROOT", root):
                entry = inventory.inventory_entry(slot)

            pattern = entry["pattern_children"][0]
            self.assertTrue(pattern["has_source"])
            self.assertIsNone(pattern["source_preview"])
            self.assertEqual(inventory.validate([entry]), [])

    def test_tier_a_research_child_contract_remains_intact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            slot = root / "15_Research_Repo_Templates"
            child = slot / "sample-research-template"
            child.mkdir(parents=True)
            (child / "README.md").write_text("# Sample\n", encoding="utf-8")
            (child / "SOURCE.txt").write_text(
                "Preferred SOURCE: https://example.test/repo\n", encoding="utf-8"
            )

            with patch.object(inventory, "ROOT", root):
                entry = inventory.inventory_entry(slot)

            self.assertTrue(entry["research_children"][0]["has_source"])
            self.assertTrue(entry["research_children"][0]["has_readme"])
            self.assertEqual(inventory.validate([entry]), [])


if __name__ == "__main__":
    unittest.main()
