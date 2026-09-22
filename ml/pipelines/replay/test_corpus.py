import unittest
from ml.pipelines.replay.corpus import project

class CorpusTests(unittest.TestCase):
    def test_project(self) -> None:
        rows = project([{"experiment_id": "x", "gain": 1, "sha": "aa"}])
        self.assertEqual(rows[0]["corpus"], "evolutionary-replay")
