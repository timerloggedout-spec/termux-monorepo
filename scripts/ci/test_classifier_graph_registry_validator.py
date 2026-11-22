"""Offline regression tests for the classifier graph registry validator."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
from classifier_graph_registry_validator import validate_registry


class ClassifierGraphRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(
            (ROOT / "config/classifier_graph_registry.json").read_text(encoding="utf-8")
        )
        cls.catalog = json.loads(
            (ROOT / "config/system_one_catalog.json").read_text(encoding="utf-8")
        )

    def validate(self, registry):
        return validate_registry(ROOT, registry, self.catalog)

    def test_checked_in_registry_is_valid(self):
        self.assertEqual(self.validate(copy.deepcopy(self.registry)), [])

    def test_unknown_catalog_reference_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        candidate = next(item for item in registry["candidates"] if item["kind"] == "catalog")
        candidate["catalog_entry_id"] = "S1-DOES-NOT-EXIST"
        self.assertTrue(any("unknown catalog entry" in error for error in self.validate(registry)))

    def test_candidate_role_mismatch_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        node = registry["graphs"][0]["nodes"][0]
        node["role_id"] = "typed_decision"
        self.assertTrue(any("does not implement role" in error for error in self.validate(registry)))

    def test_dependency_cycle_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        nodes = registry["graphs"][0]["nodes"]
        nodes[0]["depends_on"] = ["reducer"]
        self.assertTrue(any("dependency cycle" in error for error in self.validate(registry)))

    def test_duplicate_node_identity_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        nodes = registry["graphs"][0]["nodes"]
        nodes[1]["node_id"] = nodes[0]["node_id"]
        self.assertTrue(any("duplicate node ID" in error for error in self.validate(registry)))


if __name__ == "__main__":
    unittest.main()
