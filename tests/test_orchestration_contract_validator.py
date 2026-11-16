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

    def test_malformed_nested_property_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schema_dir = root / "docs" / "ops"
            schema_dir.mkdir(parents=True)
            treatment = json.loads((ROOT / "docs" / "ops" / "ORCHESTRATION-TREATMENT.schema.json").read_text())
            treatment["properties"]["status"] = None
            (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(json.dumps(treatment))
            (schema_dir / "ORCHESTRATION-RECEIPT.schema.json").write_text("not json")
            skill_dir = root / ".agents" / "skills" / "orchestration-treatment-registry"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("references")

            errors = validate_contracts(root)
            self.assertTrue(any("status lifecycle enum drifted" in error for error in errors))
            self.assertTrue(any("cannot read valid JSON" in error for error in errors))

    def test_malformed_top_level_schema_structures_are_reported_without_crashing(self):
        cases = (
            ("properties", None, "properties must be an object"),
            ("properties", [], "properties must be an object"),
            ("properties", "bad", "properties must be an object"),
            ("required", None, "required must be a string array"),
            ("required", "bad", "required must be a string array"),
            ("required", [{}], "required must be a string array"),
        )
        for key, value, diagnostic in cases:
            with self.subTest(key=key, value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    schema_dir = root / "docs" / "ops"
                    schema_dir.mkdir(parents=True)
                    treatment = json.loads((ROOT / "docs/ops/ORCHESTRATION-TREATMENT.schema.json").read_text())
                    treatment[key] = value
                    (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(json.dumps(treatment))
                    receipt = ROOT / "docs/ops/ORCHESTRATION-RECEIPT.schema.json"
                    (schema_dir / "ORCHESTRATION-RECEIPT.schema.json").write_text(receipt.read_text())
                    skill_dir = root / ".agents/skills/orchestration-treatment-registry"
                    skill_dir.mkdir(parents=True)
                    (skill_dir / "SKILL.md").write_text((ROOT / ".agents/skills/orchestration-treatment-registry/SKILL.md").read_text())
                    errors = validate_contracts(root)
                    self.assertTrue(any(diagnostic in error for error in errors), errors)

    def test_unhashable_enum_entries_and_nested_values_are_reported_without_crashing(self):
        for invalid in ([{}], [[], "TASK_PASS"], {"enum": [None]}):
            with self.subTest(invalid=invalid):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    schema_dir = root / "docs" / "ops"
                    schema_dir.mkdir(parents=True)
                    treatment = json.loads((ROOT / "docs/ops/ORCHESTRATION-TREATMENT.schema.json").read_text())
                    receipt = json.loads((ROOT / "docs/ops/ORCHESTRATION-RECEIPT.schema.json").read_text())
                    treatment["properties"]["status"]["enum"] = invalid if not isinstance(invalid, dict) else invalid["enum"]
                    receipt["properties"]["outcome"]["enum"] = invalid if not isinstance(invalid, dict) else invalid["enum"]
                    (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(json.dumps(treatment))
                    (schema_dir / "ORCHESTRATION-RECEIPT.schema.json").write_text(json.dumps(receipt))
                    skill_dir = root / ".agents/skills/orchestration-treatment-registry"
                    skill_dir.mkdir(parents=True)
                    (skill_dir / "SKILL.md").write_text((ROOT / ".agents/skills/orchestration-treatment-registry/SKILL.md").read_text())
                    errors = validate_contracts(root)
                    self.assertTrue(any("status lifecycle enum drifted" in error for error in errors), errors)
                    self.assertTrue(any("outcome enum drifted" in error for error in errors), errors)

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
