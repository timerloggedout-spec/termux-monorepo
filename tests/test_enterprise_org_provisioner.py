from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EnterpriseOrganizationWorkflowTests(unittest.TestCase):
    def test_repository_provisioner_preserves_personal_default_and_guards_org_creation(self) -> None:
        workflow = (ROOT / ".github/workflows/repository-provisioner.yml").read_text(encoding="utf-8")
        self.assertIn("default: timerloggedout-spec", workflow)
        self.assertIn("default: user", workflow)
        self.assertIn("- organization", workflow)
        self.assertIn('if [[ "$CREDENTIAL_REF" == "GITHUB_TOKEN" ]]', workflow)
        self.assertIn('if [[ "$membership" != "admin:active" ]]', workflow)
        self.assertIn('!= "free"', workflow)
        self.assertIn('required_confirmation="CREATE $TARGET_OWNER/$REPO_NAME"', workflow)
        self.assertIn('create_endpoint="/orgs/$TARGET_OWNER/repos"', workflow)

    def test_transfer_workflow_defaults_to_dry_run_and_requires_apply_confirmation(self) -> None:
        workflow = (ROOT / ".github/workflows/enterprise-org-repository-transfer.yml").read_text(encoding="utf-8")
        self.assertIn("default: dry_run", workflow)
        self.assertIn("baseline_run_id", workflow)
        self.assertIn("confirmation", workflow)
        self.assertIn("apply", workflow)

    def test_proposal_records_have_clean_whitespace(self) -> None:
        paths = [
            ROOT / "docs/proposals/active/enterprise-org-preservation/ITEMS.md",
            ROOT / "docs/proposals/active/enterprise-org-preservation/MANIFEST.md",
            ROOT / "docs/proposals/active/repository-provisioner/ITEMS.md",
        ]
        for path in paths:
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, [line.rstrip() for line in lines], path.as_posix())

    def test_baseline_workflow_uses_read_only_permissions(self) -> None:
        workflow = (ROOT / ".github/workflows/enterprise-org-detachment-verify.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("actions: read", workflow)
        self.assertIn("baseline", workflow)


if __name__ == "__main__":
    unittest.main()
