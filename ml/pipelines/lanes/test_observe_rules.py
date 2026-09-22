import unittest
from ml.pipelines.lanes.observe_rules import should_observe

class ObserveTests(unittest.TestCase):
    def test_draft(self) -> None:
        self.assertTrue(should_observe({"draft": True}))
