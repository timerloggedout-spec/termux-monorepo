import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from orchestration_contract_validator import validate_contracts


class OrchestrationContractValidatorTests(unittest.TestCase):
    def test_repository_contracts_pass(self):
        self.assertEqual(validate_contracts(), [])

    def test_missing_receipt_schema_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schema_dir = root / "docs" / "ops"
            schema_dir.mkdir(parents=True)
            treatment = ROOT / "docs" / "ops" / "ORCHESTRATION-TREATMENT.schema.json"
            (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(treatment.read_text())
            errors = validate_contracts(root)
            self.assertTrue(any("ORCHESTRATION-RECEIPT.schema.json" in error for error in errors))

    def test_receipt_schema_rejects_state_outcome_conflation(self):
        receipt_path = ROOT / "docs" / "ops" / "ORCHESTRATION-RECEIPT.schema.json"
        schema = json.loads(receipt_path.read_text())
        schema["properties"]["outcome"]["enum"] = ["COMPLETED", "FAILED"]
        with tempfile.TemporaryDirectory() as tmp:
            fixture_root = Path(tmp)
            (fixture_root / "docs" / "ops").mkdir(parents=True)
            skill_dir = fixture_root / ".agents" / "skills" / "orchestration-treatment-registry"
            skill_dir.mkdir(parents=True)
            for name in ("ORCHESTRATION-TREATMENT.schema.json",):
                source = ROOT / "docs" / "ops" / name
                (fixture_root / "docs" / "ops" / name).write_text(source.read_text())
            (fixture_root / "docs" / "ops" / "ORCHESTRATION-RECEIPT.schema.json").write_text(json.dumps(schema))
            skill_source = ROOT / ".agents" / "skills" / "orchestration-treatment-registry" / "SKILL.md"
            (skill_dir / "SKILL.md").write_text(skill_source.read_text())
            errors = validate_contracts(fixture_root)
            self.assertTrue(any("outcome enum drifted" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
