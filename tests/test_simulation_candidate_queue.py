"""Regression tests for the SIP alternative candidate queue and QUE route."""
import json
import unittest
from pathlib import Path

from scripts.ops.swarm_admission import parse_block, template_identity
from scripts.integrations.validate_capability_graph import validate_graph

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "docs/rfps/simulation-intelligence-plane/candidate-queue.json"
TEMPLATE = ROOT / ".github/ISSUE_TEMPLATE/simulation-rfp.yml"
GRAPH = ROOT / "docs/integrations/capability-opportunity-graph.json"


class SimulationCandidateQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = json.loads(QUEUE.read_text(encoding="utf-8"))
        cls.template_text = TEMPLATE.read_text(encoding="utf-8")

    def test_candidate_ids_are_unique_and_required_alternatives_present(self):
        candidates = self.queue["candidates"]
        ids = [item["id"] for item in candidates]
        self.assertEqual(len(ids), len(set(ids)))
        expected = {
            "mirofish", "mirofish-refactor-fork", "camel-ai-oasis", "mesa", "repast", "netlogo",
            "deterministic-fake", "langgraph", "temporal", "autogen",
            "crewai", "openai-agents-sdk",
        }
        self.assertTrue(expected.issubset(set(ids)))

    def test_existing_capabilities_are_not_recast_as_new_integrations(self):
        by_id = {item["id"]: item for item in self.queue["candidates"]}
        self.assertEqual(by_id["langgraph"]["status"], "existing_repo_work")
        self.assertEqual(by_id["temporal"]["status"], "existing_repo_work_and_prior_rfp")
        self.assertEqual(by_id["mesa"]["status"], "existing_research_reference")
        self.assertEqual(by_id["netlogo"]["status"], "existing_research_reference")

    def test_roles_keep_unlike_candidates_separate(self):
        by_id = {item["id"]: item for item in self.queue["candidates"]}
        self.assertEqual(by_id["camel-ai-oasis"]["class"], "social-simulation-engine")
        self.assertEqual(by_id["langgraph"]["class"], "agent-orchestration-framework")
        self.assertEqual(by_id["temporal"]["class"], "durable-workflow-runtime")
        self.assertEqual(by_id["mirofish"]["class"], "graph-to-simulation-workbench-reference")

    def test_candidate_queue_is_projected_into_ceel_graph(self):
        graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.assertEqual(validate_graph(graph), [])
        graph_ids = {node["id"] for node in graph["nodes"]}
        queue_ids = {item["id"] for item in self.queue["candidates"]}
        self.assertTrue(queue_ids.issubset(graph_ids))
        self.assertIn("simulation-intelligence-plane", graph_ids)

    def test_issue_template_declares_que_admission_route(self):
        block = parse_block(self.template_text)
        labels, prefix = template_identity(self.template_text)
        self.assertIsNotNone(block)
        self.assertEqual(block["schema"], "issue-dispatch/v1")
        self.assertEqual(block["lane"], "simulation-intelligence-plane")
        self.assertEqual(block["que_tier"], 2)
        self.assertEqual(block["route"], "simulation-rfp-intake.yml")
        self.assertTrue(prefix.startswith("[simulation:rfp]"))


if __name__ == "__main__":
    unittest.main()
