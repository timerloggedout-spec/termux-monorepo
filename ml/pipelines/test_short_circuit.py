import unittest
from ml.pipelines.lanes.short_circuit import may_promote
from ml.pipelines.lanes.vocab import Lane

class ShortCircuitTest(unittest.TestCase):
    def test_only_candidate(self) -> None:
        self.assertTrue(may_promote(Lane.CANDIDATE))
        self.assertFalse(may_promote(Lane.EXTRACT))
        self.assertFalse(may_promote(Lane.NEED_EVIDENCE))
        self.assertFalse(may_promote(Lane.SUPERSEDE))

if __name__ == "__main__":
    unittest.main()
