import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("nomenclature_validator", ROOT / "scripts/ci/validate_nomenclature_matrix.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SEED = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/seed.json"

class NomenclatureMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SEED.read_text(encoding="utf-8"))

    def test_seed_validates(self):
        self.assertEqual([], MODULE.validate(self.data))

    def test_monomials_and_mappings_resolve(self):
        concepts = {c["concept_id"] for c in self.data["concepts"]}
        sources = {s["source_id"] for s in self.data["sources"]}
        for label in self.data["labels"]:
            self.assertIn(label["concept_id"], concepts)
            self.assertTrue(set(label["source_ids"]) <= sources)
        for mapping in self.data["mappings"]:
            self.assertIn(mapping["source_concept_id"], concepts)
            self.assertIn(mapping["target_concept_id"], concepts)

    def test_exact_match_cannot_be_accepted_without_sources(self):
        bad = json.loads(json.dumps(self.data))
        bad["mappings"][0].update(relation="exact_match", status="accepted", source_ids=[])
        self.assertTrue(any("requires evidence" in e for e in MODULE.validate(bad)))

    def test_hidden_search_alias_is_a_supported_label_type(self):
        data = json.loads(json.dumps(self.data))
        data["labels"][0]["label_type"] = "hidden_search_alias"
        self.assertEqual([], MODULE.validate(data))

    def test_expanded_seed_covers_colloquial_mapping_and_near_synonymy(self):
        concepts = {c["concept_id"] for c in self.data["concepts"]}
        self.assertIn("terminology.colloquial_to_formal_mapping", concepts)
        self.assertIn("linguistics.near_synonymy", concepts)
        self.assertGreaterEqual(len(self.data["sources"]), 8)

    def test_unknown_label_type_rejected(self):
        bad = json.loads(json.dumps(self.data))
        bad["labels"][0]["label_type"] = "just-a-synonym"
        self.assertTrue(any("invalid type/status" in e for e in MODULE.validate(bad)))

if __name__ == "__main__":
    unittest.main()
