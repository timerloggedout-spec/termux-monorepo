import unittest

from she.metrics.tdqs import (
    apply_post_processing,
    context_signals,
    overall_server_score,
    server_definition_quality,
    tier,
    weighted_score,
)


class TDQSTests(unittest.TestCase):
    def setUp(self):
        self.tool = {
            "name": "search_docs",
            "title": "Search project documentation",
            "description": "Search project documentation by query and optional scope.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Terms to search for."},
                    "scope": {"type": "string", "enum": ["repo", "docs"], "description": "Search scope."},
                },
                "required": ["query"],
            },
            "outputSchema": {
                "type": "object",
                "properties": {"matches": {"type": "array"}},
            },
            "annotations": {"readOnlyHint": True, "openWorldHint": False},
        }

    def test_context_signals_are_deterministic(self):
        first = context_signals(self.tool)
        second = context_signals(self.tool)
        self.assertEqual(first, second)
        self.assertEqual(first.param_count, 2)
        self.assertEqual(first.required_param_count, 1)
        self.assertEqual(first.params_with_descriptions, 2)
        self.assertEqual(first.params_with_enums, 1)
        self.assertEqual(first.schema_description_coverage, 100)
        self.assertEqual(first.required_field_count, 1)
        self.assertEqual(first.schema_depth, 1)
        self.assertEqual(first.invocation_cost, 1)
        self.assertTrue(first.has_output_schema)
        self.assertTrue(first.has_annotations)
        self.assertEqual(len(first.input_hash), 16)

    def test_missing_description_is_hard_gate(self):
        tool = dict(self.tool, description=" ")
        result = apply_post_processing(tool, {})
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["tier"], "D")
        self.assertIn("No Description", result["flags"])
        self.assertTrue(all(value == 1.0 for value in result["dimensions"].values()))

    def test_tautological_description_caps_purpose(self):
        tool = dict(self.tool, description="search_docs")
        dimensions = {
            "purpose_clarity": 5,
            "usage_guidelines": 5,
            "behavioral_transparency": 5,
            "parameter_semantics": 5,
            "conciseness_structure": 5,
            "contextual_completeness": 5,
        }
        result = apply_post_processing(tool, dimensions)
        self.assertEqual(result["dimensions"]["purpose_clarity"], 2.0)
        self.assertIn("Tautological Description", result["flags"])
        self.assertEqual(result["score"], 4.3)

    def test_weighted_score_and_tiers(self):
        dimensions = {name: 3 for name in (
            "purpose_clarity", "usage_guidelines", "behavioral_transparency",
            "parameter_semantics", "conciseness_structure", "contextual_completeness",
        )}
        self.assertEqual(weighted_score(dimensions), 3.0)
        self.assertEqual(tier(3.5), "A")
        self.assertEqual(tier(3.0), "B")
        self.assertEqual(tier(2.0), "C")
        self.assertEqual(tier(1.0), "D")
        self.assertEqual(tier(0.9), "F")

    def test_server_rollups(self):
        self.assertEqual(server_definition_quality([4.0, 3.0, 5.0]), 3.6)
        self.assertEqual(overall_server_score(3.6, 4.0), 3.7)

    def test_nested_required_subtree_cost(self):
        tool = dict(self.tool)
        tool["inputSchema"] = {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "mode": {"type": "string", "enum": ["a", "b"]},
                    },
                    "required": ["query", "mode"],
                }
            },
            "required": ["payload"],
        }
        signals = context_signals(tool)
        self.assertEqual(signals.required_field_count, 3)
        self.assertEqual(signals.schema_depth, 2)
        self.assertEqual(signals.invocation_cost, 5)


if __name__ == "__main__":
    unittest.main()
