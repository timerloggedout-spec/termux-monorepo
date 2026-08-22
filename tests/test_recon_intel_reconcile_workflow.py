from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "recon-intel-reconcile.yml"


class ReconIntelReconcileWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_reconciliation_is_manual_and_explicitly_confirmed(self) -> None:
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertNotIn("schedule:", self.workflow)
        self.assertIn("github.event.inputs.apply == 'true'", self.workflow)
        self.assertIn("GitHub default branch changed; a fresh RECON INTEL observation is required.", self.workflow)

    def test_only_manual_apply_job_has_narrow_write_permissions(self) -> None:
        self.assertIn("permissions: {}", self.workflow)
        self.assertIn("contents: write", self.workflow)
        self.assertIn("pull-requests: write", self.workflow)
        self.assertNotIn("issues: write", self.workflow)
        self.assertNotIn("actions: write", self.workflow)

    def test_exact_fresh_tuple_and_allowlisted_ref_are_required(self) -> None:
        self.assertIn("options: [master]", self.workflow)
        self.assertIn("Only GitLab master is allowlisted.", self.workflow)
        self.assertIn("INPUT_GITLAB_SHA", self.workflow)
        self.assertIn("GitLab changed; a fresh exact SHA tuple is required.", self.workflow)
        self.assertIn("fresh gitlab-ahead observation", self.workflow)

    def test_workflow_fails_closed_without_history_rewrite_or_gitlab_write(self) -> None:
        self.assertIn("git merge --abort || true", self.workflow)
        self.assertIn("requires a manual conflict-resolution plan; no branch was pushed", self.workflow)
        self.assertNotIn("git push --force", self.workflow)
        self.assertNotIn("git reset --hard", self.workflow)
        self.assertNotIn("gitlab.com/api", self.workflow)
        self.assertIn("did not update GitLab, force-push, auto-merge, or synthesize conflict resolution", self.workflow)

    def test_branch_and_pr_are_deterministic_and_idempotent(self) -> None:
        self.assertIn("sync/gitlab/${short_github}-${short_gitlab}", self.workflow)
        self.assertIn("refusing duplicate preparation", self.workflow)
        self.assertIn("Reusing open reconciliation PR", self.workflow)
        self.assertIn("Implements: AR-17", self.workflow)


if __name__ == "__main__":
    unittest.main()
