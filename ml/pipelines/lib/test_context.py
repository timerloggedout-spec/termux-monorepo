import unittest

from ml.pipelines.lib.context import prs, put, snapshot


class ContextTests(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(snapshot({}), {})
        self.assertEqual(prs({}), [])

    def test_put(self) -> None:
        ctx: dict = {"snapshot": {"prs": [{"number": 1}]}}
        put(ctx, "n", 3)
        self.assertEqual(ctx["n"], 3)
        self.assertEqual(len(prs(ctx)), 1)
