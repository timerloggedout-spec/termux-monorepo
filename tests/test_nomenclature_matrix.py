import importlib.util
import json
import sqlite3
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

    def test_schema_and_validator_agree_on_hidden_search_alias(self):
        schema = (ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/schema.sql").read_text(encoding="utf-8")
        self.assertIn("hidden_search_alias", schema)
        self.assertIn("hidden_search_alias", MODULE.LABEL_TYPES)

    def test_sqlite_schema_executes_and_has_evidence_table(self):
        schema = (ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/schema.sql").read_text(encoding="utf-8")
        connection = sqlite3.connect(":memory:")
        try:
            connection.executescript(schema)
            columns = {row[1] for row in connection.execute("PRAGMA table_info(evidence_records)")}
            self.assertTrue({"evidence_id", "source_id", "assertion_type", "assertion_id", "claim", "evidence_locator", "evidence_excerpt", "retrieved_on", "reviewer", "status"} <= columns)
        finally:
            connection.close()

    def test_expanded_seed_covers_colloquial_mapping_and_near_synonymy(self):
        concepts = {c["concept_id"] for c in self.data["concepts"]}
        self.assertIn("terminology.colloquial_to_formal_mapping", concepts)
        self.assertIn("linguistics.near_synonymy", concepts)
        self.assertGreaterEqual(len(self.data["sources"]), 8)

    def test_evidence_records_have_source_locator_excerpt_and_date(self):
        self.assertGreaterEqual(len(self.data["evidence_records"]), 1)
        for evidence in self.data["evidence_records"]:
            self.assertTrue(evidence["source_id"])
            self.assertTrue(evidence["evidence_locator"])
            self.assertTrue(evidence["evidence_excerpt"])
            self.assertRegex(evidence["retrieved_on"], r"^\d{4}-\d{2}-\d{2}$")

    def test_evidence_cannot_reference_unknown_assertion(self):
        bad = json.loads(json.dumps(self.data))
        bad["evidence_records"][0]["assertion_id"] = "missing-label"
        self.assertTrue(any("unknown assertion" in e for e in MODULE.validate(bad)))

    def test_accepted_evidence_requires_reviewer(self):
        bad = json.loads(json.dumps(self.data))
        bad["evidence_records"][0].update(status="accepted", reviewer=None)
        self.assertTrue(any("requires reviewer" in e for e in MODULE.validate(bad)))

    def test_unknown_label_type_rejected(self):
        bad = json.loads(json.dumps(self.data))
        bad["labels"][0]["label_type"] = "just-a-synonym"
        self.assertTrue(any("invalid type/status" in e for e in MODULE.validate(bad)))

if __name__ == "__main__":
    unittest.main()
