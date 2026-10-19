"""Contract tests for ATES explicit skip receipts."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-throughput-evidence.yml"


class AtESkipReceiptContractTests(unittest.TestCase):
    def test_non_emission_creates_and_uploads_an_outcome_receipt(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Emit explicit ATES outcome receipt", source)
        self.assertIn("Upload ATES outcome receipt", source)
        self.assertIn("ates.observation.v1", source)
        self.assertIn("metrics_emitted", source)
        self.assertIn("missing_evidence_policy", source)

    def test_rate_limit_and_unmapped_workflow_are_classified(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("core.setOutput('skip_reason', 'rate_limited')", source)
        self.assertIn("core.setOutput('skip_reason', 'unmapped_workflow')", source)

    def test_skip_receipt_does_not_fabricate_metrics(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"metrics_emitted": False', source)
        self.assertIn('"status": ("failed" if os.environ["COLLECT_OUTCOME"]', source)
        self.assertIn('"collection_outcome": os.environ["COLLECT_OUTCOME"]', source)
        self.assertIn('"deferred" if os.environ["SKIP_REASON"] == "rate_limited"', source)
        self.assertIn('"unknown remains unknown; no metrics inferred"', source)

    def test_emitted_receipt_marks_missing_evidence_as_partial(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"status": "partial" if evidence_gaps else "emitted"', source)
        self.assertIn('"task_boundary_artifact_missing"', source)
        self.assertIn('"task_complexity_unavailable"', source)


if __name__ == "__main__":
    unittest.main()
