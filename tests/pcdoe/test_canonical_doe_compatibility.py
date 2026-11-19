import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
POLICIES = json.loads((ROOT / "docs/ops/pcdoe/PRIORITIZATION-POLICIES.json").read_text())
EXPERIMENT_SCHEMA = json.loads((ROOT / "docs/ops/corpus/EXPERIMENT.schema.json").read_text())
TOURNAMENT_SCHEMA = json.loads((ROOT / "docs/ops/MANAGER-TOURNAMENT.schema.json").read_text())


class CanonicalDoECompatibilityTests(unittest.TestCase):
    def test_policy_treatments_map_to_existing_manager_tournament_contract(self):
        managers = [
            {
                "manager_id": policy["policy_id"],
                "policy_hash": __import__("hashlib").sha256(
                    json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
                "routing_policy": None,
            }
            for policy in POLICIES["policies"]
        ]
        tournament = {
            "schema_version": "manager.tournament.v1",
            "tournament_id": "pcdoe-008-schema-compatibility",
            "cohort_id": "fixture-only",
            "policy_version": "pcdoe-008-v1",
            "task_contract_hash": "fixture-task-contract-sha256",
            "environment_fingerprint": "fixture-environment",
            "managers": managers,
            "evaluation_contract": {
                "acceptance": "Schema compatibility only; no treatment execution.",
                "evidence_schema": "docs/ops/corpus/EXPERIMENT.schema.json",
                "repetitions": 1,
            },
            "provenance": {
                "created_at": "2026-11-19T00:00:00Z",
                "repository_sha": "d8e973825db98d6cda6cfbd37d8b1350fe1ebea2",
                "benchmark_source": None,
            },
        }
        Draft202012Validator.check_schema(TOURNAMENT_SCHEMA)
        Draft202012Validator(TOURNAMENT_SCHEMA).validate(tournament)
        self.assertEqual(len(tournament["managers"]), 6)

    def test_policy_identity_maps_to_existing_experiment_record_contract(self):
        policy = POLICIES["policies"][0]
        experiment = {
            "schema_version": "1.0",
            "experiment_id": "pcdoe-008-schema-compatibility-fixture",
            "observed_at": "2026-11-19T00:00:00Z",
            "baseline_sha": "0" * 40,
            "candidate_sha": "1" * 40,
            "suite": "pcdoe-008-schema-compatibility-fixture",
            "cohort": "fixture-only",
            "treatment": {
                "manager_policy_id": policy["policy_id"],
                "arm": policy["policy_id"],
            },
            "status": "skipped",
            "outcome": None,
            "provenance": "manual",
            "confidence": "low",
        }
        Draft202012Validator.check_schema(EXPERIMENT_SCHEMA)
        Draft202012Validator(EXPERIMENT_SCHEMA).validate(experiment)
        self.assertEqual(experiment["treatment"]["manager_policy_id"], policy["policy_id"])
        self.assertEqual(experiment["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
