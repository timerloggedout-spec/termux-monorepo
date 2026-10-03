"""Tests for deepcli._v1_hindsight_tools - tool registry + merge invariant."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deepcli import _v1_hindsight_tools as ht  # noqa: E402


class TestHindsightTools(unittest.TestCase):
    def setUp(self):
        self._saved = os.environ.get("HINDSIGHT_TOOLS_ENABLED")

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("HINDSIGHT_TOOLS_ENABLED", None)
        else:
            os.environ["HINDSIGHT_TOOLS_ENABLED"] = self._saved

    def test_disabled_returns_empty(self):
        os.environ["HINDSIGHT_TOOLS_ENABLED"] = "0"
        self.assertFalse(ht.hindsight_enabled())
        self.assertEqual(ht.hindsight_tools(), [])

    def test_disabled_merge_is_passthrough(self):
        os.environ["HINDSIGHT_TOOLS_ENABLED"] = ""
        caller = [{"type": "function", "function": {"name": "foo", "parameters": {}}}]
        out = ht.merge_into(caller)
        self.assertEqual(out, caller)
        self.assertIsNot(out, caller)  # new list, no aliasing

    def test_enabled_exposes_three_tools(self):
        os.environ["HINDSIGHT_TOOLS_ENABLED"] = "1"
        specs = ht.hindsight_tools()
        names = {s["function"]["name"] for s in specs}
        self.assertEqual(names, set(ht.HINDSIGHT_TOOL_NAMES))
        for s in specs:
            self.assertEqual(s["type"], "function")
            self.assertIn("parameters", s["function"])

    def test_merge_is_pure_and_idempotent(self):
        os.environ["HINDSIGHT_TOOLS_ENABLED"] = "true"
        caller = [{"type": "function", "function": {"name": "mine", "parameters": {}}}]
        merged = ht.merge_into(caller)
        self.assertEqual(len(caller), 1)  # caller untouched
        names = [t["function"]["name"] for t in merged]
        self.assertEqual(names.count("hindsight_recall"), 1)
        again = ht.merge_into(merged)
        self.assertEqual(
            sorted(t["function"]["name"] for t in again),
            sorted(t["function"]["name"] for t in merged),
        )

    def test_caller_definition_wins_on_name_collision(self):
        os.environ["HINDSIGHT_TOOLS_ENABLED"] = "yes"
        caller = [
            {
                "type": "function",
                "function": {
                    "name": "hindsight_recall",
                    "description": "MINE",
                    "parameters": {},
                },
            }
        ]
        merged = ht.merge_into(caller)
        hit = [t for t in merged if t["function"]["name"] == "hindsight_recall"]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]["function"]["description"], "MINE")

    def test_invoke_unknown_tool(self):
        os.environ["HINDSIGHT_TOOLS_ENABLED"] = "1"
        import asyncio

        res = asyncio.run(ht.invoke("nope", {}))
        self.assertFalse(res["ok"])
        self.assertIn("unknown", res["error"])


if __name__ == "__main__":
    unittest.main()
