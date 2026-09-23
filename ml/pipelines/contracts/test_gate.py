"""Promote-gate tests."""
from __future__ import annotations

import unittest

from ml.pipelines.contracts.gate import assert_promotable
from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.types import Lane


class TestGate(unittest.TestCase):
    def test_blocks_wait(self) -> None:
        with self.assertRaises(GateBlocked):
            assert_promotable({"dual_gate": "green", "mergeable_state": "clean"}, Lane.WAIT)

    def test_allows_promote(self) -> None:
        assert_promotable({"dual_gate": "green", "mergeable_state": "clean"}, Lane.PROMOTE)


if __name__ == "__main__":
    unittest.main()
