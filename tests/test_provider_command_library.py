from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = ROOT / ".github" / "agentic" / "provider-command-library.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "provider-command-dispatch.yml"


class ProviderCommandLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.library = json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_library_declares_known_provider_action_sets(self) -> None:
        providers = self.library["providers"]
        self.assertIn("review_full", providers["coderabbit"]["commands"])
        self.assertIn("autofix_current", providers["coderabbit"]["commands"])
        self.assertIn("fix_ci_current", providers["coderabbit"]["commands"])
        self.assertIn("resolve_merge_conflict", providers["coderabbit"]["commands"])
        self.assertEqual("/agentic_review", providers["qodo"]["commands"]["review"]["documented_command"])
        self.assertEqual("/devin review", providers["devin"]["commands"]["review"]["documented_command"])

    def test_branch_writing_actions_require_explicit_dispatch_confirmation(self) -> None:
        commands = self.library["providers"]["coderabbit"]["commands"]
        for action in ("autofix_current", "autofix_stacked", "fix_ci_current", "fix_ci_stacked", "resolve_merge_conflict"):
            self.assertTrue(commands[action]["requires_confirm_branch_write"], action)
        self.assertIn("confirm_branch_write=true is required", self.workflow)

    def test_dispatcher_reads_only_default_branch_library_and_checks_live_head_sha(self) -> None:
        self.assertIn("ref: defaultBranch", self.workflow)
        self.assertIn("if (pr.head.sha !== requestedSha)", self.workflow)
        self.assertIn("Stale head SHA", self.workflow)
        self.assertNotIn("actions/checkout", self.workflow)

    def test_dispatcher_uses_control_before_documented_command_and_records_receipt(self) -> None:
        self.assertIn("execution_order", LIBRARY_PATH.read_text(encoding="utf-8"))
        self.assertIn("github.rest.issues.updateComment", self.workflow)
        self.assertIn("using documented command", self.workflow)
        self.assertIn("<!-- operator-provider-command:v1 -->", self.workflow)
        self.assertIn("Already dispatched ${provider}:${action}", self.workflow)

    def test_control_patch_is_limited_to_trusted_provider_authors_and_declared_labels(self) -> None:
        self.assertIn("providerEntry.authors.includes(author)", self.workflow)
        self.assertIn("labels.includes(candidate[3].trim())", self.workflow)
        self.assertIn("checkboxId", self.workflow)


if __name__ == "__main__":
    unittest.main()
