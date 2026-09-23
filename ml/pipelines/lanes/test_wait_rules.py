import unittest
from ml.pipelines.lanes.wait_rules import should_wait

class WaitTests(unittest.TestCase):
    def test_724(self) -> None:
        self.assertTrue(should_wait({"mergeable_state": "unstable", "dual_gate": "green"}))

    def test_hitl_not_wait(self) -> None:
        self.assertFalse(should_wait({"mergeable_state": "unstable", "hitl_risk": True}))
