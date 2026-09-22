import unittest
from ml.pipelines.replay.action_effect import import_events

class ActionEffectTests(unittest.TestCase):
    def test_import(self) -> None:
        rows = import_events([{"sha": "d10a7a54", "outcome": "PASS", "kind": "help-wanted"}])
        self.assertEqual(rows[0]["outcome"], "PASS")
