"""Dependency-free structural checks for BIUDL machine-readable contracts."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "schemas"

CONTRACTS = {
    "capability-registration.schema.json": {
        "capability_id", "version", "owner_lane", "operation",
        "input_schema_ref", "output_schema_ref", "required_scopes",
        "approval_policy", "idempotency", "availability", "lifecycle",
    },
    "collaborator-lifecycle.schema.json": {
        "collaborator_id", "identity", "declared_roles", "adapter_refs",
        "lifecycle", "provenance", "updated_at",
    },
    "firesight-finding.schema.json": {
        "finding_id", "fingerprint", "detector", "severity", "state",
        "summary", "evidence_refs", "first_observed_at", "last_observed_at",
    },
    "component-release-manifest.schema.json": {
        "component_id", "version", "source", "released_at", "contracts",
        "dependencies", "validation", "promotion",
    },
}


class BIUDLContractSchemaTests(unittest.TestCase):
    def test_all_contract_schemas_are_present_and_parse(self):
        for filename in CONTRACTS:
            with self.subTest(schema=filename):
                path = SCHEMA_DIR / filename
                self.assertTrue(path.is_file(), f"Missing schema: {path}")
                with path.open(encoding="utf-8") as stream:
                    schema = json.load(stream)
                self.assertEqual(
                    schema.get("$schema"),
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertEqual(schema.get("type"), "object")
                self.assertIs(schema.get("additionalProperties"), False)

    def test_required_contract_fields_exist(self):
        for filename, expected in CONTRACTS.items():
            with self.subTest(schema=filename):
                with (SCHEMA_DIR / filename).open(encoding="utf-8") as stream:
                    schema = json.load(stream)
                properties = schema.get("properties", {})
                required = set(schema.get("required", []))
                self.assertTrue(expected.issubset(required))
                self.assertTrue(required.issubset(properties))
                self.assertEqual(schema.get("schema_version", {}).get("const"), "1.0")

    def test_contract_schema_ids_are_unique(self):
        ids = []
        for filename in CONTRACTS:
            with (SCHEMA_DIR / filename).open(encoding="utf-8") as stream:
                ids.append(json.load(stream).get("$id"))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(ids))


if __name__ == "__main__":
    unittest.main()
