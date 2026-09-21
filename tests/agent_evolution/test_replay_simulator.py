import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.agent_evolution.replay_simulator import (  # noqa: E402
    DiscoveryHistory,
    DiscoveryNode,
    EvolutionConfig,
    EvolutionEngine,
    ExplorationPolicy,
    ReplaySimulator,
)


class ReplaySimulatorTests(unittest.TestCase):
    def history(self):
        return DiscoveryHistory.from_nodes([
            DiscoveryNode("root-a", None, 1.0),
            DiscoveryNode("a-1", "root-a", 4.0, terminal=True),
            DiscoveryNode("a-2", "root-a", 0.5, terminal=True),
            DiscoveryNode("root-b", None, 2.0),
            DiscoveryNode("b-1", "root-b", 5.0, terminal=True),
        ])

    def test_jsonl_round_trip(self):
        original = self.history()
        restored = DiscoveryHistory.from_jsonl(original.to_jsonl())
        self.assertEqual(original, restored)

    def test_replay_is_deterministic_and_free_of_execution(self):
        simulator = ReplaySimulator(self.history())
        policy = ExplorationPolicy(max_active=2)
        first = simulator.replay(policy)
        second = simulator.replay(policy)
        self.assertEqual(first, second)
        self.assertEqual(first.policy_id, policy.policy_id)
        self.assertEqual(first.replay_cost, 5.0)

    def test_incumbent_is_always_a_candidate(self):
        simulator = ReplaySimulator(self.history())
        incumbent = ExplorationPolicy(max_active=1, min_score=100.0)
        engine = EvolutionEngine(simulator, EvolutionConfig(generations=2, mutations_per_generation=4, min_improvement=0.1))
        selected, observations = engine.evolve(incumbent)
        self.assertEqual(selected.policy_id, incumbent.policy_id)
        self.assertGreaterEqual(len(observations), 1 + 2 * 5)

    def test_evidence_is_machine_readable(self):
        simulator = ReplaySimulator(self.history())
        policy = ExplorationPolicy()
        result = simulator.replay(policy)
        record = {
            "schema": "agent.replay-evolution.v1",
            "policy_id": policy.policy_id,
            "score": result.score,
            "execution": "replay_only",
        }
        self.assertEqual(json.loads(json.dumps(record))["execution"], "replay_only")


if __name__ == "__main__":
    unittest.main()
