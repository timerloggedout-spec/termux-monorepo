import unittest
from ml.pipelines.contracts.gate import block_reasons, assert_promotable
from ml.pipelines.lib.errors import GateBlocked

class GateTest(unittest.TestCase):
    def test_blocks_dirty(self) -> None:
        reasons = block_reasons({"mergeable_state": "dirty", "base": {"ref": "master"}})
        self.assertIn("mergeable_state=dirty", reasons)
    def test_assert(self) -> None:
        with self.assertRaises(GateBlocked):
            assert_promotable({"number": 48, "base": {"ref": "master-staging"}})

if __name__ == "__main__":
    unittest.main()
