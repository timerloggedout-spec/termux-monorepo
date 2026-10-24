"""Offline contract tests for the deterministic Delphi Oracle MVP."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.delphi.strands_oracle_mvp import (
    ContractError,
    DEFAULT_FIXTURES,
    deterministic_oracle,
    load_fixtures,
    run_experiments,
    validate_receipt,
)


class DelphiOracleMVPTests(unittest.TestCase):
    def test_three_experiments_share_one_fixture_hash_and_rubric(self):
        receipt = run_experiments(DEFAULT_FIXTURES, "a" * 40)
        self.assertEqual({item["id"] for item in receipt["experiments"]}, {"E-01", "E-03", "E-05"})
        self.assertEqual({item["fixture_hash"] for item in receipt["experiments"]}, {receipt["fixture_sha256"]})
        self.assertEqual({item["rubric_version"] for item in receipt["experiments"]}, {"delphi-oracle-rubric/v1"})
        self.assertTrue(all(item["result"] == "PASS" for item in receipt["experiments"]))

    def test_consequential_actions_always_escalate(self):
        fixtures, _ = load_fixtures(DEFAULT_FIXTURES)
        for case in fixtures["cases"]:
            if case["action"] in {"merge", "release", "credential_mutation", "delete", "deploy", "provision", "paid_fallback"}:
                self.assertEqual(deterministic_oracle(case), "ESCALATE", case["id"])

    def test_material_and_irrelevant_counterfactuals(self):
        receipt = run_experiments(DEFAULT_FIXTURES, "b" * 40)
        e03 = next(item for item in receipt["experiments"] if item["id"] == "E-03")
        self.assertTrue(e03["metrics"]["material_evidence_changes_decision"])
        self.assertTrue(e03["metrics"]["irrelevant_change_preserves_decision"])

    def test_adversarial_instruction_never_authorizes_deploy(self):
        receipt = run_experiments(DEFAULT_FIXTURES, "c" * 40)
        case = next(row for row in receipt["case_results"] if row["case_id"] == "injection-requests-deploy")
        self.assertTrue(case["adversarial_fixture"])
        self.assertEqual(case["oracle_decision"], "ESCALATE")
        self.assertTrue(case["baseline_unsafe_pass_through"])

    def test_receipt_is_explicit_about_absent_votes_and_cloud_execution(self):
        receipt = run_experiments(DEFAULT_FIXTURES, "d" * 40)
        self.assertEqual(receipt["human_ballots_received"], 0)
        self.assertEqual(receipt["provider_results_received"], 0)
        self.assertFalse(receipt["deployment"])
        self.assertEqual(receipt["aws_invocations"], 0)
        self.assertIsNone(receipt["measured_cloud_cost_usd"])
        self.assertFalse(receipt["state"]["PROMOTED"])
        validate_receipt(receipt)

    def test_bad_url_scheme_is_rejected(self):
        fixtures, _ = load_fixtures(DEFAULT_FIXTURES)
        fixtures["cases"][0]["evidence_refs"] = ["javascript:alert(1)"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(fixtures), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "forbidden URL scheme"):
                load_fixtures(path)

    def test_receipt_cannot_claim_model_results_or_deployment(self):
        receipt = run_experiments(DEFAULT_FIXTURES, "e" * 40)
        receipt["provider_results_received"] = 1
        with self.assertRaisesRegex(ContractError, "must not be represented"):
            validate_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
