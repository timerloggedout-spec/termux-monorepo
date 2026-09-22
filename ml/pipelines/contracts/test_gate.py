import unittest

from ml.pipelines.contracts.gate import assert_promotable
from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.types import Lane


class GateTests(unittest.TestCase):
    def test_blocks_extract(self) -> None:
        with self.assertRaises(GateBlocked):
            assert_promotable({"dual_gate": "green", "mergeable_state": "clean"}, Lane.EXTRACT)

    def test_allows_promote(self) -> None:
        assert_promotable({"dual_gate": "green", "mergeable_state": "clean"}, Lane.PROMOTE)

    def test_blocks_staging(self) -> None:
        with self.assertRaises(GateBlocked):
            assert_promotable(
                {"dual_gate": "green", "mergeable_state": "clean", "master_staging_base": True},
                Lane.PROMOTE,
            )

    def test_blocks_hitl(self) -> None:
        with self.assertRaises(GateBlocked):
            assert_promotable(
                {"dual_gate": "green", "mergeable_state": "clean", "hitl_risk": True},
                Lane.PROMOTE,
            )
