import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "docs/ops/pcdoe"


class ContractSchemaTests(unittest.TestCase):
    def load_schema(self, name):
        return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))

    def test_all_contract_schemas_are_valid_json_schema_documents(self):
        for name in (
            "DO-STATEMENT.schema.json",
            "AUTOAPPROVE-POLICY.schema.json",
            "PRIORITIZATION-POLICY.schema.json",
        ):
            with self.subTest(schema=name):
                schema = self.load_schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(schema["required"])
                self.assertTrue(schema["properties"])

    def test_do_statement_requires_mandate_and_acceptance(self):
        schema = self.load_schema("DO-STATEMENT.schema.json")
        self.assertTrue({
            "statement_id", "scope", "action", "constraints", "output",
            "owner_ref", "acceptance", "evidence", "approval_class"
        }.issubset(set(schema["required"])))

    def test_autoapprove_schema_encodes_formal_approval_boundary(self):
        schema = self.load_schema("AUTOAPPROVE-POLICY.schema.json")
        formal = schema["properties"]["formal_approval_classes"]["const"]
        self.assertTrue({
            "github_review", "merge", "release", "production_promotion",
            "credential", "permission", "security_policy", "destructive_data",
            "external_commitment"
        }.issubset(set(formal)))

    def test_policy_catalog_matches_schema_treatments(self):
        catalog = json.loads((SCHEMA_DIR / "PRIORITIZATION-POLICIES.json").read_text())
        schema = self.load_schema("PRIORITIZATION-POLICY.schema.json")
        allowed = set(schema["properties"]["treatment_type"]["enum"])
        self.assertEqual(len(catalog["policies"]), 6)
        self.assertEqual(len({item["policy_id"] for item in catalog["policies"]}), 6)
        self.assertTrue(all(item["treatment_type"] in allowed for item in catalog["policies"]))


if __name__ == "__main__":
    unittest.main()
