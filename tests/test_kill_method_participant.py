"""Fail-closed contract tests for the versioned kill-method participant."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/proposals/validate_kill_method_participant.py"
SPEC = importlib.util.spec_from_file_location("kill_method_validator", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)

SCHEMA, FIXTURE = VALIDATOR.load_contract()
CULL_FIXTURE = json.loads(
    (ROOT / "docs/proposals/active/siglary-doe-kill-method-participant/fixtures/kill-method-participant.cull.valid.json").read_text()
)


class KillMethodParticipantContractTests(unittest.TestCase):
    def assert_rejected(self, record):
        self.assertTrue(VALIDATOR.validate_record(record, SCHEMA))

    def test_schema_and_fixture_are_valid_json(self):
        json.loads((ROOT / "docs/proposals/active/siglary-doe-kill-method-participant/schemas/kill-method-participant.schema.json").read_text())
        self.assertEqual([], VALIDATOR.validate_record(FIXTURE, SCHEMA))

    def test_execution_cannot_be_enabled(self):
        record = copy.deepcopy(FIXTURE)
        record["authorization"]["execution_enabled"] = True
        self.assert_rejected(record)

    def test_broad_target_selection_is_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["scope"]["selection"] = "wildcard"
        self.assert_rejected(record)

    def test_target_fanout_is_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["scope"]["max_targets"] = 100
        self.assert_rejected(record)

    def test_production_environment_is_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["scope"]["environment"] = "production"
        self.assert_rejected(record)

    def test_queue_method_only_admits_queued_runs(self):
        record = copy.deepcopy(FIXTURE)
        record["scope"]["allowed_states"] = ["in_progress"]
        self.assert_rejected(record)

    def test_queue_method_forbids_in_progress_state(self):
        record = copy.deepcopy(FIXTURE)
        record["scope"]["forbidden_states"] = ["completed"]
        self.assert_rejected(record)

    def test_wildcard_target_reference_is_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["scope"]["target_ref"] = "workflow-run:*"
        self.assert_rejected(record)

    def test_method_family_must_match_method_id(self):
        record = copy.deepcopy(FIXTURE)
        record["method"]["method_family"] = "worker_fault_injection"
        self.assert_rejected(record)

    def test_idempotency_key_contract_is_required(self):
        record = copy.deepcopy(FIXTURE)
        del record["idempotency"]["key_template"]
        self.assert_rejected(record)

    def test_dependent_work_policy_is_required(self):
        record = copy.deepcopy(FIXTURE)
        del record["impact"]["dependent_work_policy"]
        self.assert_rejected(record)

    def test_timeout_bound_is_enforced(self):
        record = copy.deepcopy(FIXTURE)
        record["preconditions"]["timeout_seconds"] = 301
        self.assert_rejected(record)

    def test_idempotency_window_bound_is_enforced(self):
        record = copy.deepcopy(FIXTURE)
        record["idempotency"]["window_seconds"] = 86401
        self.assert_rejected(record)

    def test_agentic_gambling_cull_requires_same_record_consequence(self):
        self.assertEqual([], VALIDATOR.validate_record(CULL_FIXTURE, SCHEMA))
        record = copy.deepcopy(CULL_FIXTURE)
        del record["cull_consequence"]
        self.assert_rejected(record)

    def test_cull_wallet_unknown_is_schema_null_not_not_established_marker(self):
        record = copy.deepcopy(CULL_FIXTURE)
        record["cull_consequence"]["wallet_balance_at_cull"] = "N∅"
        self.assert_rejected(record)

    def test_unknown_method_is_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["method"]["method_id"] = "kill.everything"
        self.assert_rejected(record)

    def test_unknown_schema_version_is_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["schema_version"] = "kill-method-participant.v2"
        self.assert_rejected(record)

    def test_unknown_state_is_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["preconditions"]["unknown_state_behavior"] = "guess"
        self.assert_rejected(record)

    def test_receipt_is_mandatory(self):
        record = copy.deepcopy(FIXTURE)
        record["evidence"]["receipt_required"] = False
        self.assert_rejected(record)

    def test_additional_properties_are_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["authorization"]["secret"] = "must-not-be-here"
        self.assert_rejected(record)


if __name__ == "__main__":
    unittest.main()
