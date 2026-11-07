"""Contract tests for ATES explicit outcome receipts."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-throughput-evidence.yml"
BUILDER = ROOT / "scripts" / "ci" / "ates_outcome_receipt.py"
CLI = ROOT / "scripts" / "ci" / "ates_outcome_receipt_cli.py"


class AtESkipReceiptContractTests(unittest.TestCase):
    def test_non_success_runs_are_observed_without_success_only_job_gate(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Observe every completed source run", source)
        self.assertIn("if (run.conclusion !== 'success')", source)
        self.assertNotIn("    if: github.event.workflow_run.conclusion == 'success'", source)
        self.assertIn("Emit explicit ATES outcome receipt", source)
        self.assertIn("Upload ATES outcome receipt", source)
        self.assertIn("ates_outcome_receipt_cli.py", source)

    def test_rate_limit_and_unmapped_workflow_are_classified(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("core.setOutput('skip_reason', 'rate_limited')", source)
        self.assertIn("core.setOutput('skip_reason', 'unmapped_workflow')", source)

    def test_receipt_builder_preserves_provenance_without_fabricating_metrics(self):
        source = BUILDER.read_text(encoding="utf-8")
        self.assertIn('"schema_version": "ates.observation.v1"', source)
        self.assertIn('"metrics_emitted": False', source)
        self.assertIn('"source_conclusion": source_conclusion', source)
        self.assertIn('"missing_evidence_policy": "unknown remains unknown; no metrics inferred"', source)
        self.assertIn('status = "source_non_success"', source)

    def test_cli_uses_shared_receipt_builder(self):
        source = CLI.read_text(encoding="utf-8")
        self.assertIn("build_outcome_receipt", source)
        self.assertIn("source_conclusion=args.source_conclusion", source)


if __name__ == "__main__":
    unittest.main()
