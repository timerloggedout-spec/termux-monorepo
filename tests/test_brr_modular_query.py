import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "branch_registry", "scripts/branch_reconciliation_registry.py"
)
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


class ModularSelectionTests(unittest.TestCase):
    def test_profiles_stack_with_explicit_surfaces(self):
        selected = registry.selected_surfaces(
            ["reconciliation", "architecture"], ["issue"], False, False
        )
        self.assertTrue({"branch", "pull-request", "file", "symbol", "scope", "issue"} <= selected)

    def test_ast_and_similarity_add_their_required_surfaces(self):
        selected = registry.selected_surfaces([], [], True, True)
        self.assertEqual(selected, {"branch", "pull-request", "file", "symbol"})

    def test_default_profile_preserves_legacy_inventory(self):
        self.assertEqual(
            registry.selected_surfaces([], [], False, False),
            {"branch", "pull-request"},
        )

    def test_query_clauses_support_all_and_any(self):
        record = {"branch": "release/alpha", "sha": "abc123"}
        self.assertTrue(registry.matches_queries(record, ["release", "abc"], "all"))
        self.assertFalse(registry.matches_queries(record, ["release", "missing"], "all"))
        self.assertTrue(registry.matches_queries(record, ["missing", "abc"], "any"))

    def test_graph_projection_keeps_similarity_as_candidate_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nodes.jsonl").write_text(
                json.dumps({"kind": "file", "external_id": "src/a.py", "attributes": {"path": "src/a.py"}})
                + "\n"
                + json.dumps({"kind": "symbol", "external_id": "src/a.py:run", "attributes": {"name": "run"}})
                + "\n",
                encoding="utf-8",
            )
            (root / "edges.jsonl").write_text(
                json.dumps({
                    "id": "candidate-1",
                    "type": "CO_CHANGED_WITH",
                    "source": "file:src/a.py",
                    "target": "file:src/b.py",
                    "classification": "candidate",
                    "score": 0.5,
                })
                + "\n",
                encoding="utf-8",
            )
            result = registry.load_graph_projection(
                root, {"file", "symbol"}, [], "all", 10, True
            )
            self.assertEqual(result["node_count"], 2)
            self.assertEqual(result["similarity_candidate_count"], 1)
            self.assertEqual(
                result["similarity_candidates"][0]["classification"], "candidate"
            )


if __name__ == "__main__":
    unittest.main()
