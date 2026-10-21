from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/workflow-surface-policy.yml"


class AutomationDocumentationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_control_plane_paths_trigger_freshness_job(self) -> None:
        for expected in (
            "automation_docs:",
            "high_impact_control_plane:",
            "high_impact_control_plane: ${{ steps.changes.outputs.high_impact_control_plane }}",
            "scripts/model_router.py",
            "docs/schemas/model-success-matrix.yaml",
            "docs/schemas/llm-leaderboard-matrix.yaml",
            "docs/ops/diagrams/**",
            "docs/ops/generated/**",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.text)

    def test_freshness_job_is_read_only_and_checks_committed_outputs(self) -> None:
        section = self.text.split("  automation-documentation:", 1)[1]
        self.assertIn("if: needs.route.outputs.automation_docs == 'true'", section)
        self.assertIn("permissions:\n      contents: read", section)
        self.assertIn(
            "python3 -m unittest tests.test_automation_docs "
            "tests.test_automation_documentation_workflow",
            section,
        )
        self.assertIn("python3 scripts/ci/automation_docs.py --check", section)
        self.assertNotIn("pull-requests: write", section)
        self.assertNotIn("issues: write", section)
        self.assertNotIn("git push", section)
        self.assertIn("HIGH_IMPACT_CONTROL_PLANE_CHANGED", section)
        self.assertIn("high-impact control-plane review required", section)

    def test_preview_artifact_is_immutable_pinned_and_retained_briefly(self) -> None:
        section = self.text.split("  automation-documentation:", 1)[1]
        self.assertIn(
            "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
            section,
        )
        self.assertIn("name: automation-documentation-preview", section)
        self.assertIn("retention-days: 7", section)


if __name__ == "__main__":
    unittest.main()
