"""Regression tests for the disabled-by-default AWS Emulator contract."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "integrations/aws-emulator/contract.json"
VALIDATOR_PATH = ROOT / "scripts/ci/verify_aws_emulator_contract.py"


class AwsEmulatorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def validate(self, **changes):
        candidate = copy.deepcopy(self.contract)
        candidate.update(changes)
        with __import__("tempfile").TemporaryDirectory() as tmp:
            path = Path(tmp) / "contract.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATOR_PATH), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        return result

    def test_checked_in_contract_passes(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(CONTRACT_PATH)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("runtime disabled", result.stdout)

    def test_rejects_runtime_activation(self):
        self.assertNotEqual(self.validate(runtime_enabled=True).returncode, 0)

    def test_rejects_cloud_fallback(self):
        self.assertNotEqual(self.validate(cloud_fallback="allow").returncode, 0)

    def test_rejects_non_loopback_endpoint(self):
        self.assertNotEqual(
            self.validate(endpoint="https://example.com:9297").returncode, 0
        )

    def test_rejects_ambient_credentials(self):
        self.assertNotEqual(self.validate(credentials="ambient_aws_chain").returncode, 0)

    def test_rejects_production_scope(self):
        self.assertNotEqual(self.validate(production_allowed=True).returncode, 0)

    def test_rejects_security_testing_claim(self):
        self.assertNotEqual(self.validate(security_testing_allowed=True).returncode, 0)

    def test_rejects_unknown_schema(self):
        self.assertNotEqual(
            self.validate(schema_version="aws-emulator-integration.v2").returncode, 0
        )

    def test_rejects_missing_required_gate(self):
        self.assertNotEqual(
            self.validate(required_gates=["unit_tests"]).returncode, 0
        )

    def test_rejects_missing_production_deny(self):
        self.assertNotEqual(
            self.validate(forbidden_environments=["developer_local"]).returncode, 0
        )


if __name__ == "__main__":
    unittest.main()
