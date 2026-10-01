import unittest

from scripts.agent_evolution.replay_simulator import DiscoveryHistory, DiscoveryNode, ExplorationPolicy, ReplaySimulator
from scripts.agent_evolution.corpus_projection import to_experiment_record


class CorpusProjectionTests(unittest.TestCase):
    BASE = "a" * 40
    HEAD = "b" * 40

    def result(self):
        history = DiscoveryHistory.from_nodes([
            DiscoveryNode("root", None, 2.0),
            DiscoveryNode("leaf", "root", 5.0, terminal=True),
        ])
        return ReplaySimulator(history).replay(ExplorationPolicy(max_active=2))

    def test_projection_matches_experiment_contract_shape(self):
        policy = ExplorationPolicy(max_active=2)
        record = to_experiment_record(
            experiment_id="replay-001", observed_at="2026-09-22T13:00:00Z",
            baseline_sha=self.BASE, candidate_sha=self.HEAD, suite="evolutionary-replay",
            policy=policy, result=self.result(), cohort="cohort-1",
            provider="provider-a", model="model-a", outcome="replay_candidate_observed",
            evidence_refs=["https://example.invalid/evidence/1"],
        )
        self.assertEqual(record["schema_version"], "1.0")
        self.assertEqual(record["baseline_sha"], self.BASE)
        self.assertEqual(record["candidate_sha"], self.HEAD)
        self.assertEqual(record["treatment"]["manager_policy_id"], policy.policy_id)
        self.assertEqual(record["treatment"]["arm"], "replay")
        self.assertEqual(record["metrics"]["terminal_count"], 1)

    def test_projection_rejects_unanchored_sha(self):
        with self.assertRaises(ValueError):
            to_experiment_record(experiment_id="replay-002", observed_at="2026-09-22T13:00:00Z",
                                 baseline_sha="not-a-sha", candidate_sha=self.HEAD,
                                 suite="evolutionary-replay", policy=ExplorationPolicy(), result=self.result())

    def test_projection_defaults_to_observed_without_outcome(self):
        record = to_experiment_record(experiment_id="replay-003", observed_at="2026-09-22T13:00:00Z",
                                      baseline_sha=self.BASE, candidate_sha=self.HEAD,
                                      suite="evolutionary-replay", policy=ExplorationPolicy(), result=self.result())
        self.assertEqual(record["status"], "observed")
        self.assertIsNone(record["outcome"])
        self.assertEqual(record["confidence"], "medium")


if __name__ == "__main__":
    unittest.main()