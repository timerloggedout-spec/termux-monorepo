import unittest

from ml.pipelines.contracts.promote import promote_packet
from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.types import Lane


class PromoteTests(unittest.TestCase):
    def test_packet(self) -> None:
        packet = promote_packet(
            {"number": 707, "changed_files": 3, "dual_gate": "green", "mergeable_state": "clean"},
            Lane.PROMOTE,
        )
        self.assertEqual(packet["decision"], "promote")

    def test_oversize(self) -> None:
        with self.assertRaises(GateBlocked):
            promote_packet(
                {"number": 48, "changed_files": 73, "dual_gate": "green", "mergeable_state": "clean"},
                Lane.PROMOTE,
            )
