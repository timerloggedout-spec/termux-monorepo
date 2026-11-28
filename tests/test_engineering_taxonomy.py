from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from ops.engineering.taxonomy import load_taxonomy, validate
from scripts.engineering.toolchain_probe import build_report


class EngineeringTaxonomyTests(TestCase):
    def test_taxonomy_and_toolchains_validate(self):
        taxonomy = load_taxonomy()
        self.assertEqual(validate(taxonomy), [])
        self.assertGreaterEqual(len(taxonomy["toolchains"]), 4)

    def test_all_tool_nodes_have_a_parent_and_access_record(self):
        taxonomy = load_taxonomy()
        for node in taxonomy["nodes"]:
            if node["kind"] == "tool":
                self.assertTrue(node["parents"])
                self.assertIn(node["metadata"]["access"], taxonomy["axes"]["access"])
                self.assertTrue(node["metadata"]["source_url"])

    def test_polyhierarchy_with_multiple_valid_parents_is_accepted(self):
        taxonomy = deepcopy(load_taxonomy())
        taxonomy["nodes"].append({
            "id": "mechanical-electronics-interface",
            "kind": "category",
            "name": "Mechanical-electronics interface",
            "parents": ["mechanical-engineering", "electronics-engineering"],
            "tags": {"discipline": ["mechanical", "electronics"]},
        })
        self.assertEqual(validate(taxonomy), [])

    def test_unknown_parent_is_rejected(self):
        taxonomy = deepcopy(load_taxonomy())
        taxonomy["nodes"].append({
            "id": "orphan-tool",
            "kind": "tool",
            "name": "Orphan",
            "parents": ["missing-parent"],
            "tags": {"tool_role": ["parametric-cad"]},
            "metadata": {
                "license": "MIT",
                "license_class": "foss",
                "access": "local-free",
                "payment_card_required": "false",
                "execution_target": "local-or-remote",
                "probe_commands": [],
                "source_url": "https://example.invalid/",
            },
        })
        self.assertTrue(any("unknown parent" in error for error in validate(taxonomy)))

    def test_probe_reports_executable_presence_without_running_tools(self):
        taxonomy = load_taxonomy()
        with patch("scripts.engineering.toolchain_probe.shutil.which", side_effect=lambda name: name if name == "kicad-cli" else None):
            report = build_report(taxonomy)
        self.assertEqual(report["schema"], "engineering-toolchain-probe/v1")
        self.assertEqual(report["summary"]["catalogued"], len([n for n in taxonomy["nodes"] if n["kind"] == "tool"]))
        kicad = next(item for item in report["tools"] if item["id"] == "kicad")
        self.assertTrue(kicad["detected"])
        self.assertEqual(kicad["matched_command"], "kicad-cli")

    def test_integration_registry_and_reference_catalog_are_enrolled(self):
        root = Path(__file__).resolve().parents[1]
        integrations = json.loads((root / "docs/integrations/registry.json").read_text(encoding="utf-8"))
        entry = next(item for item in integrations["integrations"] if item["id"] == "engineering-toolchains")
        self.assertEqual(entry["repo_skill_path"], ".agents/skills/engineering-toolchains/SKILL.md")
        references = json.loads((root / "docs/ops/ENGINEERING-REFERENCE-SET.json").read_text(encoding="utf-8"))
        self.assertEqual(references["schema"], "engineering-reference-set/v1")
        self.assertEqual(len(references["references"]), 20)
        self.assertTrue(all(item["state"] == "reference-only" for item in references["references"]))

    def test_archwiz_cockpit_exposes_read_only_engineering_inventory(self):
        root = Path(__file__).resolve().parents[1]
        cockpit = (root / "archwiz/termux_cockpit.py").read_text(encoding="utf-8")
        self.assertIn("[21] Engineering Toolchain Inventory", cockpit)
        self.assertIn('if choice == "21"', cockpit)
        self.assertIn("scripts" + ' / "engineering" / "toolchain_probe.py"', cockpit)

    def test_free_tier_and_paid_product_are_separate_classes(self):
        taxonomy = load_taxonomy()
        by_id = {node["id"]: node for node in taxonomy["nodes"]}
        self.assertEqual(by_id["onshape-free"]["metadata"]["access"], "cloud-free-tier")
        self.assertEqual(by_id["onshape-free"]["metadata"]["commercial_use"], "restricted")
        self.assertEqual(by_id["onshape-free"]["metadata"]["payment_card_required"], "unknown")
        self.assertEqual(by_id["solidworks-makers"]["metadata"]["access"], "commercial-paid")
        self.assertEqual(by_id["solidworks"]["metadata"]["payment_card_required"], "unknown")
        self.assertTrue(all(node["metadata"]["payment_card_required"] is False for node in by_id.values() if node["kind"] == "tool" and node["metadata"]["license_class"] == "foss"))


if __name__ == "__main__":
    import unittest
    unittest.main()
