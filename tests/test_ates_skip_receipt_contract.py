"""Contract tests for ATES outcome receipts and workflow admission."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-throughput-evidence.yml"
BUILDER = ROOT / "scripts" / "ci" / "ates_outcome_receipt.py"
CLI = ROOT / "scripts" / "ci" / "ates_outcome_receipt_cli.py"


class AtESkipReceiptContractTests(unittest.TestCase):
    def test_non_success_runs_reach_observer_and_upload_receipt(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Observe every completed source run", source)
        self.assertNotIn("    if: github.event.workflow_run.conclusion == 'success'", source)
        self.assertIn("if (run.conclusion !== 'success')", source)
        self.assertIn("core.setOutput('skip_reason', 'source_non_success')", source)
        self.assertIn("Emit explicit ATES outcome receipt", source)
        self.assertIn("Upload ATES outcome receipt", source)
        self.assertIn("SOURCE_CONCLUSION:", source)

    def test_rate_limit_and_unmapped_workflow_are_classified(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("core.setOutput('skip_reason', 'rate_limited')", source)
        self.assertIn("core.setOutput('skip_reason', 'unmapped_workflow')", source)

    def test_receipt_builder_and_cli_are_the_single_receipt_path(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        builder = BUILDER.read_text(encoding="utf-8")
        cli = CLI.read_text(encoding="utf-8")
        self.assertIn("ates_outcome_receipt_cli.py", workflow)
        self.assertIn('"schema_version": "ates.observation.v1"', builder)
        self.assertIn('"metrics_emitted": False', builder)
        self.assertIn('"missing_evidence_policy": "unknown remains unknown; no metrics inferred"', builder)
        self.assertIn("build_outcome_receipt", cli)
        self.assertIn("source_conclusion=args.source_conclusion", cli)

    def test_success_path_still_emits_metric_evidence(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Emit sanitized ATES JSONL", source)
        self.assertIn("Build evidence receipt", source)
        self.assertIn("agent-throughput-metrics.json", source)


if __name__ == "__main__":
    unittest.main()
