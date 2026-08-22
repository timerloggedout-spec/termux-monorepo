from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "recon-intel-discovery.yml"


class ReconIntelWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_workflow_has_read_only_default_permissions_and_no_mutation_api(self) -> None:
        self.assertIn("permissions: {}", self.workflow)
        self.assertNotIn("contents: write", self.workflow)
        self.assertNotIn("pull-requests: write", self.workflow)
        self.assertNotIn("issues: write", self.workflow)
        self.assertNotIn("issues.createComment", self.workflow)
        self.assertNotIn("issues.updateComment", self.workflow)
        self.assertNotIn("pulls.create", self.workflow)
        self.assertNotIn("git.createRef", self.workflow)

    def test_schedule_and_idle_probe_do_not_expand_write_authority(self) -> None:
        self.assertIn("- cron: '*/15 * * * *'", self.workflow)
        self.assertIn("now.getUTCMinutes() === 0 && now.getUTCHours() % 6 === 0", self.workflow)
        self.assertIn("allow_scheduled_repository_writes", (ROOT / ".github" / "agentic" / "recon-intel-policy.json").read_text(encoding="utf-8"))
        self.assertIn("This workflow is read-only", self.workflow)

    def test_workflow_uses_trusted_default_branch_and_never_checks_out_pr_code(self) -> None:
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)
        self.assertIn("refs/pull/${TARGET_PR_NUMBER}/head:refs/recon-intel/github/pr/${TARGET_PR_NUMBER}", self.workflow)
        self.assertIn("Target changed during discovery; refusing stale comparison.", self.workflow)

    def test_gitlab_ref_and_manual_pr_input_are_allowlisted(self) -> None:
        self.assertIn("options: [master]", self.workflow)
        self.assertIn("gitlabRef !== 'master'", self.workflow)
        self.assertIn("pr_number must be a positive decimal integer", self.workflow)
        self.assertIn("open, non-draft, same-repository pull request", self.workflow)

    def test_gitlab_token_is_used_only_for_classification(self) -> None:
        self.assertIn("RECON_INTEL_GITLAB_READ_TOKEN", self.workflow)
        self.assertIn("secrets.GITLAB_TOKEN", self.workflow)
        self.assertIn("secrets.OPERATOR_GITLAB_TOKEN", self.workflow)
        self.assertIn("python3 scripts/ci/recon_intel_discovery.py", self.workflow)
        self.assertNotIn("gitlab.com/a-group2180532/termux-monorepo.git", self.workflow)


if __name__ == "__main__":
    unittest.main()
