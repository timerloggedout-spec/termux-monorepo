import unittest
from pathlib import Path

from scripts.ci.workflow_run_contract import missing_workflow_run_workflows, scan_workflows


class WorkflowRunContractTest(unittest.TestCase):
    def test_omitted_workflows_is_a_finding(self) -> None:
        text = "name: broken\non:\n  workflow_run:\n    types: [completed]\njobs: {}\n"
        findings = missing_workflow_run_workflows(text)
        self.assertEqual(len(findings), 1)
        self.assertIn("omits required workflows", findings[0])

    def test_present_workflows_is_clean(self) -> None:
        text = (
            "name: ok\n"
            "on:\n"
            "  workflow_run:\n"
            "    workflows: [repo gate]\n"
            "    types: [completed]\n"
            "jobs: {}\n"
        )
        self.assertEqual(missing_workflow_run_workflows(text), [])

    def test_push_only_is_clean(self) -> None:
        text = "name: push\non:\n  push:\n    branches: [master]\njobs: {}\n"
        self.assertEqual(missing_workflow_run_workflows(text), [])

    def test_repo_workflows_currently_declare_workflows(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(scan_workflows(root), [])


if __name__ == "__main__":
    unittest.main()
