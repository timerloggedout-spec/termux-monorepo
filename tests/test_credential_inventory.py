import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CredentialInventoryContractTests(unittest.TestCase):
    def test_schema_json(self):
        path = ROOT / "schemas/ops/credential-surface.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Names-only credential surface")
        self.assertFalse(schema.get("additionalProperties", True))

    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/ops/validate_credential_inventory.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_no_secret_fields_in_inventory(self):
        forbidden = {"value", "token", "secret", "password", "api_key", "private_key"}
        path = ROOT / "data/ops/credential-surfaces.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            self.assertTrue(forbidden.isdisjoint(row))
            self.assertEqual(row["issue"], 184)


if __name__ == "__main__":
    unittest.main()
