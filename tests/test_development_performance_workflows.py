from __future__ import annotations

from pathlib import Path
from unittest import TestCase, main

ROOT = Path(__file__).parents[1]
SWE_WORKFLOW = (ROOT / ".github/workflows/swe-reference-evaluation.yml").read_text(encoding="utf-8")
REPOSITORY_WORKFLOW = (ROOT / ".github/workflows/repository-development-evaluation.yml").read_text(
    encoding="utf-8"
)
CONTRACT_WORKFLOW = (ROOT / ".github/workflows/development-performance-contract.yml").read_text(
    encoding="utf-8"
)


class DevelopmentPerformanceWorkflowTests(TestCase):
    def test_swe_secret_is_not_job_scoped_or_available_to_installation_steps(self):
        before_run = SWE_WORKFLOW.split("- name: Run one bounded benchmark instance", maxsplit=1)[0]
        self.assertNotIn("SWE_EVALUATION_API_KEY:", before_run)
        self.assertIn("SWE_EVALUATION_API_KEY: ${{ secrets.SWE_EVALUATION_API_KEY }}", SWE_WORKFLOW)
        self.assertIn("if: inputs.run_external_reference && vars.SWE_REFERENCE_EVALUATION_ENABLED == 'true'", SWE_WORKFLOW)
        self.assertIn("Checkout pinned mini-SWE-agent reference without provider credentials", SWE_WORKFLOW)
        self.assertIn("Install pinned reference dependencies without provider credentials", SWE_WORKFLOW)

    def test_swe_workflow_is_manual_and_bounded(self):
        self.assertIn("workflow_dispatch:", SWE_WORKFLOW)
        self.assertIn("--slice \"0:1\"", SWE_WORKFLOW)
        self.assertIn("timeout-minutes: 60", SWE_WORKFLOW)
        self.assertIn("retention-days: 14", SWE_WORKFLOW)
        self.assertNotIn("schedule:", SWE_WORKFLOW)

    def test_repository_workflow_preserves_read_only_same_repository_collection(self):
        self.assertIn("pull-requests: read", REPOSITORY_WORKFLOW)
        self.assertIn("issues: read", REPOSITORY_WORKFLOW)
        self.assertIn("checks: read", REPOSITORY_WORKFLOW)
        self.assertIn("head.repo.fork == false", REPOSITORY_WORKFLOW)
        self.assertNotIn("issues: write", REPOSITORY_WORKFLOW)
        self.assertNotIn("pull-requests: write", REPOSITORY_WORKFLOW)

    def test_repository_workflow_uses_provider_qualified_fresh_check_identity(self):
        self.assertIn("const providerId = check.app?.id || check.app?.slug || 'unknown';", REPOSITORY_WORKFLOW)
        self.assertIn("const identity = `${providerId}:${check.name}`;", REPOSITORY_WORKFLOW)
        self.assertIn("check.completed_at || check.started_at || check.created_at", REPOSITORY_WORKFLOW)

    def test_repository_workflow_paginates_threads_and_trust_binds_markers(self):
        self.assertIn("pageInfo { hasNextPage endCursor }", REPOSITORY_WORKFLOW)
        self.assertIn("} while (after);", REPOSITORY_WORKFLOW)
        self.assertIn("AUTOMATION_MARKER_PUBLISHER_LOGINS", REPOSITORY_WORKFLOW)
        self.assertIn("trustedPublishers.has", REPOSITORY_WORKFLOW)
        self.assertIn("duplicate_automation_marker_count", REPOSITORY_WORKFLOW)

    def test_contract_workflow_has_no_hard_coded_integration_branch(self):
        self.assertNotIn("master-staging", CONTRACT_WORKFLOW)
        self.assertNotIn("push:", CONTRACT_WORKFLOW)
        self.assertIn("workflow_dispatch:", CONTRACT_WORKFLOW)
        self.assertIn("tests/test_development_performance_workflows.py", CONTRACT_WORKFLOW)


if __name__ == "__main__":
    main()
