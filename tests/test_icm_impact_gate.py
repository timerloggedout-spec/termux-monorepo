"""Contract tests for the repository ICM impact gate."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci import icm_impact_gate


class ICMImpactGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs/icm/objects/governance").mkdir(parents=True)
        (self.root / "docs/icm/changes").mkdir(parents=True)
        (self.root / "scripts/ci").mkdir(parents=True)
        (self.root / "docs/icm/objects/governance/change-control.md").write_text(
            "# Change Control\n", encoding="utf-8"
        )
        (self.root / "scripts/ci/icm_impact_gate.py").write_text(
            "# gate\n", encoding="utf-8"
        )
        (self.root / "tests").mkdir()
        (self.root / "tests/test_icm_impact_gate.py").write_text(
            "# tests\n", encoding="utf-8"
        )
        (self.root / ".github/workflows").mkdir(parents=True)
        (self.root / ".github/workflows/repo-gate.yml").write_text(
            "name: repo gate\n", encoding="utf-8"
        )
        self.paths = [
            ".github/workflows/repo-gate.yml",
            "docs/icm/changes/icm-08.json",
            "docs/icm/objects/governance/change-control.md",
            "scripts/ci/icm_impact_gate.py",
            "tests/test_icm_impact_gate.py",
        ]
        self.receipt = {
            "schema_version": 1,
            "change_id": "icm-08",
            "disposition": "updated",
            "changed_paths": sorted(self.paths),
            "primary_cards": ["docs/icm/objects/governance/change-control.md"],
            "related_updates": [".github/workflows/repo-gate.yml"],
            "rationale": "The repository gate now requires an auditable ICM impact decision.",
        }
        self.write_receipt()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_receipt(self) -> None:
        (self.root / "docs/icm/changes/icm-08.json").write_text(
            json.dumps(self.receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_valid_updated_receipt_passes(self) -> None:
        self.assertEqual(icm_impact_gate.validate_receipt(self.root, self.paths), [])

    def test_missing_receipt_fails_closed(self) -> None:
        errors = icm_impact_gate.validate_receipt(
            self.root, [path for path in self.paths if path != "docs/icm/changes/icm-08.json"]
        )
        self.assertTrue(any("exactly one changed" in error for error in errors))

    def test_receipt_must_cover_exact_delta(self) -> None:
        self.receipt["changed_paths"].remove("tests/test_icm_impact_gate.py")
        self.write_receipt()
        errors = icm_impact_gate.validate_receipt(self.root, self.paths)
        self.assertTrue(any("omits" in error for error in errors))

    def test_updated_disposition_requires_changed_primary_card(self) -> None:
        self.receipt["primary_cards"] = []
        self.write_receipt()
        errors = icm_impact_gate.validate_receipt(self.root, self.paths)
        self.assertTrue(any("requires at least one primary" in error for error in errors))

    def test_no_map_change_requires_rationale_and_existing_card(self) -> None:
        paths = [p for p in self.paths if p != "docs/icm/objects/governance/change-control.md"]
        self.receipt.update({
            "disposition": "no-map-change",
            "changed_paths": sorted(paths),
            "primary_cards": ["docs/icm/objects/governance/change-control.md"],
            "rationale": "The changed test-only fixture does not alter documented architecture.",
        })
        self.write_receipt()
        self.assertEqual(icm_impact_gate.validate_receipt(self.root, paths), [])

    def test_related_update_must_be_in_delta(self) -> None:
        self.receipt["related_updates"] = ["docs/icm/CONTEXT.md"]
        self.write_receipt()
        errors = icm_impact_gate.validate_receipt(self.root, self.paths)
        self.assertTrue(any("not changed in this PR" in error for error in errors))

    def test_path_traversal_is_rejected(self) -> None:
        self.receipt["primary_cards"] = ["docs/icm/../../outside.md"]
        self.write_receipt()
        errors = icm_impact_gate.validate_receipt(self.root, self.paths)
        self.assertTrue(any("safe repository-relative" in error for error in errors))

    def test_unsupported_receipt_fields_fail_closed(self) -> None:
        self.receipt["waiver"] = True
        self.write_receipt()
        errors = icm_impact_gate.validate_receipt(self.root, self.paths)
        self.assertTrue(any("unsupported receipt keys" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
