import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "workflows"))

from validate_wfc import validate_contract


def valid_contract():
    return {
        "schema_version": "wfc/v1",
        "workflow_id": "repo.routing-benchmark",
        "objective": "Improve verified task utility",
        "scope": {
            "repository": "owner/repo",
            "base_sha": "a" * 40,
            "cohort": "test-cohort"
        },
        "tasks": [
            {"id": "prepare", "type": "prepare", "depends_on": []},
            {"id": "execute", "type": "execute", "depends_on": ["prepare"]},
            {"id": "verify", "type": "verify", "depends_on": ["execute"]}
        ],
        "constraints": {"max_parallel": 2, "external_writes": "approval_required"},
        "success": ["outcome == PASS"],
        "evidence": ["sha", "run_id"]
    }


class WorkflowContractValidatorTests(unittest.TestCase):
    def test_valid_contract_passes(self):
        self.assertEqual(validate_contract(valid_contract()), [])

    def test_duplicate_task_id_is_rejected(self):
        data = valid_contract()
        data["tasks"].append({"id": "prepare", "type": "other", "depends_on": []})
        self.assertTrue(any("duplicate task identifier" in e for e in validate_contract(data)))

    def test_unresolved_dependency_is_rejected(self):
        data = valid_contract()
        data["tasks"][1]["depends_on"] = ["missing"]
        self.assertTrue(any("unresolved dependency" in e for e in validate_contract(data)))

    def test_dependency_cycle_is_rejected(self):
        data = valid_contract()
        data["tasks"][0]["depends_on"] = ["verify"]
        self.assertTrue(any("contains a cycle" in e for e in validate_contract(data)))

    def test_self_dependency_is_rejected(self):
        data = valid_contract()
        data["tasks"][0]["depends_on"] = ["prepare"]
        self.assertTrue(any("cannot depend on itself" in e for e in validate_contract(data)))

    def test_boolean_is_not_accepted_as_integer_budget_or_parallelism(self):
        data = valid_contract()
        data["constraints"]["max_parallel"] = True
        data["constraints"]["budget"] = {"unit": "requests", "limit": True}
        errors = validate_contract(data)
        self.assertTrue(any("max_parallel" in e for e in errors))
        self.assertTrue(any("budget.limit" in e for e in errors))

    def test_non_finite_budget_is_rejected(self):
        data = valid_contract()
        data["constraints"]["budget"] = {"unit": "requests", "limit": float("nan")}
        self.assertTrue(any("budget.limit" in e for e in validate_contract(data)))

    def test_invalid_sha_and_missing_evidence_are_rejected(self):
        data = valid_contract()
        data["scope"]["base_sha"] = "not-a-sha"
        data["evidence"] = []
        errors = validate_contract(data)
        self.assertTrue(any("base_sha" in e for e in errors))
        self.assertTrue(any("evidence:" in e for e in errors))

    def test_non_object_root_is_rejected(self):
        self.assertTrue(validate_contract([]))


if __name__ == "__main__":
    unittest.main()
