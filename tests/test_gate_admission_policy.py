"""Regression tests for surface-aware gate admission and workflow wiring."""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.ci.gate_admission import decide_admission, termux_smoke_required

ROOT = Path(__file__).resolve().parents[1]


class TermuxSurfaceClassifierTests(unittest.TestCase):
    def test_exact_runtime_files_admit_smoke(self):
        self.assertTrue(termux_smoke_required(["scripts/ci/termux_smoke.py"]))
        self.assertTrue(termux_smoke_required(["tests/fixtures/sim-memory-smoke.jsonl"]))

    def test_surface_prefixes_admit_smoke(self):
        self.assertTrue(termux_smoke_required(["archwiz/probe.py"]))
        self.assertTrue(termux_smoke_required(["deepcli/main.py"]))
        self.assertTrue(termux_smoke_required([".github/connectors/catalog.json"]))

    def test_unrelated_paths_keep_smoke_inapplicable(self):
        self.assertFalse(termux_smoke_required(["docs/notes.md", "apps/tribute-dashboard/index.html"]))
        self.assertFalse(termux_smoke_required([]))

    def test_missing_path_evidence_fails_closed(self):
        self.assertTrue(termux_smoke_required(None))
        required, reason = decide_admission("pull_request", None)
        self.assertTrue(required)
        self.assertIn("diff unavailable", reason)

    def test_manual_dispatch_runs_smoke(self):
        required, reason = decide_admission("workflow_dispatch", [])
        self.assertTrue(required)
        self.assertIn("manual", reason)


class WorkflowAdmissionContractTests(unittest.TestCase):
    def test_termux_check_stays_visible_and_smoke_steps_are_conditional(self):
        text = (ROOT / ".github/workflows/termux-smoke.yml").read_text()
        self.assertIn("pull_request:", text)
        self.assertIn("scripts/ci/gate_admission.py", text)
        self.assertIn("id: admission", text)
        self.assertIn("if: steps.admission.outputs.required == 'true'", text)
        self.assertIn("Termux surface unchanged", text)
        self.assertNotIn("Bucket headroom unit", text)
        self.assertNotIn("pip install", text)

    def test_bucket_contract_has_its_own_path_scope(self):
        text = (ROOT / ".github/workflows/bucket-headroom-contract.yml").read_text()
        for path in (
            "scripts/ops/bucket_headroom.py",
            "tests/test_bucket_headroom.py",
            "tests/test_bucket_headroom_workflow.py",
            ".github/workflows/bucket-headroom-watch.yml",
        ):
            self.assertIn(path, text)

    def test_dangle_trigger_covers_reference_targets(self):
        text = (ROOT / ".github/workflows/archwiz-dangle.yml").read_text()
        for path in (
            "docs/**", "scripts/**", "ops/**", "workspace/**", "archwiz/**",
            ".agents/**", "config/**", "tests/**", "integrations/**",
        ):
            self.assertIn(path, text)
        self.assertIn("--scope .github/ --scope apps/", text)

    def test_repo_gate_remains_universal(self):
        text = (ROOT / ".github/workflows/repo-gate.yml").read_text()
        self.assertIn("pull_request:\n    types:", text)
        self.assertIn("test_gate_admission_policy.py", text)


if __name__ == "__main__":
    unittest.main()
