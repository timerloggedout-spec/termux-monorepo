"""Eval metrics tests."""
from __future__ import annotations

import unittest

from ml.pipelines.eval.metrics import accuracy, promote_precision


class TestMetrics(unittest.TestCase):
    def test_accuracy(self) -> None:
        self.assertEqual(accuracy(["wait", "hold"], ["wait", "hold"]), 1.0)

    def test_promote_precision(self) -> None:
        self.assertEqual(promote_precision(["promote", "wait"], ["hold", "wait"]), 0.0)
        self.assertEqual(promote_precision(["promote", "promote"], ["promote", "wait"]), 0.5)


if __name__ == "__main__":
    unittest.main()
