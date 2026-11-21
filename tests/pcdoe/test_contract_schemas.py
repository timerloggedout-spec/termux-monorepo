import json
import unittest

from jsonschema import Draft202012Validator
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
            "OPTION-POSTERIOR-OBSERVATION.schema.json",
        ):
            with self.subTest(schema=name):
                schema = self.load_schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(schema["required"])
                self.assertTrue(schema["properties"])
                Draft202012Validator.check_schema(schema)

    def test_human_review_is_a_provenance_preserving_posterior_observation(self):
        schema = self.load_schema("OPTION-POSTERIOR-OBSERVATION.schema.json")
        observation = {
            "schema_version": "pcdoe.option-posterior-observation.v1",
            "observation_id": "human-review-001",
            "observation_type": "human_doe_review",
            "option_id": "priority-balanced",
            "option_version": 1,
            "assessment": {
                "dimension": "design_validity",
                "finding": "mixed",
                "rationale": "Blocking is plausible; replication assumptions need calibration."
            },
            "confidence": 0.65,
            "reviewer_ref": "reviewer://doe-independent",
            "reviewer_role": "independent_doe_reviewer",
            "cohort_ref": "cohort://fixture",
            "snapshot_ref": "snapshot://fixture",
            "observed_at": "2026-11-19T15:00:00Z",
            "evidence_refs": ["artifact://design-review"],
            "posterior_use": "pending_calibration"
        }
        Draft202012Validator(schema).validate(observation)

    def test_posterior_inclusion_requires_calibrated_likelihood_model(self):
        schema = self.load_schema("OPTION-POSTERIOR-OBSERVATION.schema.json")
        observation = {
            "schema_version": "pcdoe.option-posterior-observation.v1",
            "observation_id": "human-review-002",
            "observation_type": "human_doe_review",
            "option_id": "priority-balanced",
            "option_version": 1,
            "assessment": {"dimension": "overall", "finding": "supports"},
            "confidence": 0.8,
            "reviewer_ref": "reviewer://doe-independent",
            "reviewer_role": "independent_doe_reviewer",
            "snapshot_ref": "snapshot://fixture",
            "observed_at": "2026-11-19T15:00:00Z",
            "evidence_refs": [],
            "posterior_use": "included"
        }
        with self.assertRaises(Exception):
            Draft202012Validator(schema).validate(observation)
        observation["likelihood_model_ref"] = "calibration://human-review-v1"
        Draft202012Validator(schema).validate(observation)

    def test_policy_catalog_validates_against_prioritization_schema(self):
        schema = self.load_schema("PRIORITIZATION-POLICY.schema.json")
        catalog = json.loads((SCHEMA_DIR / "PRIORITIZATION-POLICIES.json").read_text())
        validator = Draft202012Validator(schema)
        for policy in catalog["policies"]:
            with self.subTest(policy=policy["policy_id"]):
                validator.validate(policy)

    def test_do_statement_requires_mandate_and_acceptance(self):
        schema = self.load_schema("DO-STATEMENT.schema.json")
        self.assertTrue({
            "statement_id", "scope", "action", "constraints", "output",
            "owner_ref", "acceptance", "evidence", "approval_class"
        }.issubset(set(schema["required"])))

    def test_do_statement_instance_validates(self):
        schema = self.load_schema("DO-STATEMENT.schema.json")
        instance = {
            "schema_version": "pcdoe.do-statement.v1",
            "statement_id": "fixture-001",
            "scope": "tests/pcdoe",
            "action": "Run the isolated PCDOE test suite",
            "constraints": ["Read-only fixture inputs", "Existing CI permissions only"],
            "output": "JUnit-compatible test result",
            "state": "proposed",
            "owner_ref": "PCDOE-008",
            "acceptance": ["All contract tests pass"],
            "evidence": [{"kind": "test-result", "required": True}],
            "approval_class": "preauthorized_low_risk",
            "created_at": "2026-11-19T00:00:00Z",
            "updated_at": "2026-11-19T00:00:00Z",
            "version": 1
        }
        Draft202012Validator(self.load_schema("DO-STATEMENT.schema.json")).validate(instance)

    def test_autoapprove_schema_encodes_formal_approval_boundary(self):
        schema = self.load_schema("AUTOAPPROVE-POLICY.schema.json")
        formal = schema["properties"]["formal_approval_classes"]["const"]
        self.assertTrue({
            "github_review", "merge", "release", "production_promotion",
            "credential", "permission", "security_policy", "destructive_data",
            "external_commitment"
        }.issubset(set(formal)))
        instance = {
            "schema_version": "pcdoe.autoapprove.v1",
            "policy_id": "fixture-autoapprove",
            "version": 1,
            "status": "proposed",
            "owner_ref": "PCDOE-008",
            "allowlist": [{
                "action_id": "run-tests",
                "resource_pattern": "repo://fixture/task-1",
                "actor_class": "ci-runner",
                "max_scope": "task-1-tests",
                "max_cost": 1.0,
                "timeout_seconds": 120,
                "idempotency_proof": "repeatable test command",
                "compensation": "discard isolated runner",
                "evidence_contract": "test-result",
                "owner_ref": "PCDOE-008",
                "expires_at": "2026-12-01T00:00:00Z"
            }],
            "formal_approval_classes": formal,
            "decision_record": ["decision", "reason", "evidence"]
        }
        Draft202012Validator(schema).validate(instance)

    def test_policy_catalog_matches_schema_treatments(self):
        catalog = json.loads((SCHEMA_DIR / "PRIORITIZATION-POLICIES.json").read_text())
        schema = self.load_schema("PRIORITIZATION-POLICY.schema.json")
        allowed = set(schema["properties"]["treatment_type"]["enum"])
        self.assertEqual(len(catalog["policies"]), 6)
        self.assertEqual(len({item["policy_id"] for item in catalog["policies"]}), 6)
        self.assertTrue(all(item["treatment_type"] in allowed for item in catalog["policies"]))


if __name__ == "__main__":
    unittest.main()
