from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-pr-jules-handoff.yml"


class JulesPrHandoffWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    @classmethod
    def job_block(cls, name: str) -> str:
        match = re.search(
            rf"^  {re.escape(name)}:\n.*?(?=^  [A-Za-z0-9_-]+:\n|\Z)",
            cls.workflow,
            flags=re.MULTILINE | re.DOTALL,
        )
        if match is None:
            raise AssertionError(f"job {name!r} not found")
        return match.group(0)

    def test_github_script_actions_use_immutable_commit_pins(self) -> None:
        uses = re.findall(
            r"^\s+uses:\s+([^\s#]+)",
            self.workflow,
            flags=re.MULTILINE,
        )
        self.assertGreaterEqual(len(uses), 2)
        for reference in uses:
            self.assertRegex(reference, r"^[^@\s]+@[0-9a-f]{40}$", reference)

    def test_mutation_scan_runs_only_for_pending_handoffs(self) -> None:
        mutation = self.job_block("mutation")
        self.assertIn("github.event_name == 'pull_request'", mutation)
        self.assertIn("github.event.action == 'synchronize'", mutation)
        self.assertIn(
            "contains(github.event.pull_request.labels.*.name, 'jules-handoff-pending')",
            mutation,
        )
        self.assertLess(
            mutation.index("jules-handoff-pending"),
            mutation.index("github.paginate(github.rest.issues.listComments"),
        )

    def test_trusted_handoff_arms_label_before_comment_inventory(self) -> None:
        handoff = self.job_block("handoff")
        trusted = handoff.index("if (!trustedSource) return;")
        arm = handoff.index("issues.createLabel")
        attach = handoff.index("issues.addLabels")
        inventory = handoff.index("github.paginate(github.rest.issues.listComments")
        self.assertLess(trusted, arm)
        self.assertLess(arm, attach)
        self.assertLess(attach, inventory)
        self.assertIn("jules-handoff-pending", handoff)

    def test_mutation_receipt_clears_pending_label_after_observation(self) -> None:
        mutation = self.job_block("mutation")
        comment = mutation.index("issues.createComment")
        clear = mutation.index("issues.removeLabel")
        self.assertLess(comment, clear)
        self.assertIn("MUTATION_OBSERVED", mutation)
        self.assertIn("observed_head_sha", mutation)

    def test_receipts_remain_idempotent_and_source_gated(self) -> None:
        handoff = self.job_block("handoff")
        mutation = self.job_block("mutation")
        self.assertIn("trustedSource", handoff)
        self.assertIn("trustedSource", mutation)
        self.assertIn("cs.some(c => c.user?.login === 'github-actions[bot]' && (c.body||'').includes(marker))", handoff)
        self.assertIn("cs.some(c=>c.user?.login === 'github-actions[bot]' && (c.body||'').includes(marker))", mutation)
        self.assertIn("source_comment_id", handoff)
        self.assertIn("baseline_head_sha", mutation)

    def test_dispatch_receipt_preserves_completion_and_review_gates(self) -> None:
        handoff = self.job_block("handoff")
        self.assertIn("Treat the dispatch receipt as the start of work.", handoff)
        self.assertIn("fresh exact-SHA gates", handoff)
        self.assertIn("independent verification", handoff)


if __name__ == "__main__":
    unittest.main()
