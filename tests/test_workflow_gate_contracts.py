"""YAML-backed contracts for repository gate admission workflows."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_workflow(name):
    return yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"))


def triggers(workflow):
    return workflow.get(True) or workflow.get("on") or {}


class WorkflowGateContractTests(unittest.TestCase):
    def test_repo_gate_remains_universal(self):
        workflow = load_workflow("repo-gate.yml")
        pull_request = triggers(workflow)["pull_request"]
        self.assertIsInstance(pull_request, dict)
        self.assertFalse("paths" in pull_request)
        self.assertIn("test_gate_admission_policy.py", str(workflow))

    def test_termux_check_stays_visible_and_smoke_steps_are_conditional(self):
        workflow = load_workflow("termux-smoke.yml")
        event_map = triggers(workflow)
        self.assertIn("pull_request", event_map)
        self.assertIn("push", event_map)
        self.assertIn("workflow_dispatch", event_map)
        self.assertFalse("paths" in event_map["pull_request"])

        steps = workflow["jobs"]["smoke"]["steps"]
        admission = next(step for step in steps if step.get("name") == "Determine Termux surface")
        self.assertEqual(admission.get("id"), "admission")
        required_steps = {
            "Smoke gate regression tests",
            "Core smoke (required)",
            "Optional agent-surface probes",
        }
        for step in steps:
            if step.get("name") in required_steps:
                self.assertEqual(step.get("if"), "steps.admission.outputs.required == 'true'")
        skip = next(step for step in steps if step.get("name") == "Termux surface unchanged")
        self.assertEqual(skip.get("if"), "steps.admission.outputs.required != 'true'")
        self.assertFalse(any("Bucket headroom" in step.get("name", "") for step in steps))
        self.assertFalse(any("pip install" in step.get("run", "") for step in steps))

    def test_bucket_headroom_contract_has_its_own_path_scope(self):
        workflow = load_workflow("bucket-headroom-contract.yml")
        event_map = triggers(workflow)
        paths = event_map["pull_request"]["paths"]
        for path in (
            "scripts/ops/bucket_headroom.py",
            "tests/test_bucket_headroom.py",
            ".github/workflows/bucket-headroom-watch.yml",
            ".github/workflows/bucket-headroom-contract.yml",
        ):
            self.assertIn(path, paths)
        steps = workflow["jobs"]["contract"]["steps"]
        self.assertTrue(any("pytest" in step.get("run", "") for step in steps))

    def test_dangle_trigger_covers_reference_targets(self):
        workflow = load_workflow("archwiz-dangle.yml")
        paths = triggers(workflow)["pull_request"]["paths"]
        for path in (
            "docs/**", "scripts/**", "ops/**", "workspace/**", "archwiz/**",
            ".agents/**", "config/**", "tests/**", "integrations/**",
            "deepcli/**", "deepcli-tui/**", "multi-ai-cli/**", "bin/**",
            "termux-multi-agent/**", "mcp-hub/**", "demo-portal/**",
            "README.md", "CLAUDE.md", "CLAUDE.hum.md", "AGENTS.md",
            "GEMINI.md", ".gitmodules",
        ):
            self.assertIn(path, paths)
        run_text = "\n".join(
            step.get("run", "")
            for step in workflow["jobs"]["dangle"]["steps"]
        )
        self.assertIn("--scope .github/ --scope apps/", run_text)


if __name__ == "__main__":
    unittest.main()
