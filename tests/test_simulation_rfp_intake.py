"""Tests for QUE-gated SIP RFP intake."""
import unittest

from scripts.simulation_intelligence.rfp_intake import build_intake

QUEUE = {
    "schema_version": "sip.candidate-queue.v1",
    "queue_id": "simulation-intelligence-plane-alternatives",
    "candidates": [{"id": "camel-ai-oasis"}, {"id": "mesa"}, {"id": "langgraph"}],
}

BODY = """### Candidate IDs
camel-ai-oasis
mesa

### Objective
Compare candidate engine roles.

### Research question
Which runtime best supports bounded reproducible simulations?

### Comparison dimensions
reproducibility
lifecycle recovery
cost

### Constraints and exclusions
No public writes
No paid inference

### Evidence links
https://github.com/camel-ai/oasis
docs/rfps/simulation-intelligence-plane/RFP.md

### Requested owner lane
simulation-intelligence-plane
"""


class SimulationRfpIntakeTests(unittest.TestCase):
    def test_builds_queued_intake_without_execution(self):
        record = build_intake(BODY, 5439, QUEUE)
        self.assertEqual(record["schema_version"], "sip.rfp-intake.v1")
        self.assertEqual(record["candidate_ids"], ["camel-ai-oasis", "mesa"])
        self.assertEqual(record["intake_state"], "queued_for_g0_freeze")
        self.assertFalse(record["external_calls"])
        self.assertFalse(record["provider_calls"])
        self.assertEqual(record["doe_admission"], "not_admitted_until_design_record_and_run_evidence")

    def test_unknown_candidate_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown candidate IDs"):
            build_intake(BODY.replace("mesa", "not-a-candidate"), 5439, QUEUE)

    def test_missing_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, "evidence"):
            build_intake(BODY.replace("https://github.com/camel-ai/oasis\ndocs/rfps/simulation-intelligence-plane/RFP.md", ""), 5439, QUEUE)

    def test_secret_like_value_rejected(self):
        with self.assertRaisesRegex(ValueError, "secret-like"):
            build_intake(BODY + "\napi key: ghp_" + "A" * 30, 5439, QUEUE)


if __name__ == "__main__":
    unittest.main()
