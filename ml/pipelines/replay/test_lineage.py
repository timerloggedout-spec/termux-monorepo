import unittest
from ml.pipelines.replay.lineage import lineage_fields, sufficient_gain

class LineageTests(unittest.TestCase):
    def test_gain(self) -> None:
        event = {"experiment_id": "e1", "gain": 0.2, "sha": "abc"}
        self.assertTrue(sufficient_gain(event))
        self.assertEqual(lineage_fields(event)["child_sha"], "abc")

    def test_lock_incumbent(self) -> None:
        self.assertFalse(sufficient_gain({"gain": 0.0}, floor=0.1))
