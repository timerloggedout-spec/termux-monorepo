import unittest
from ml.pipelines.replay.adapters import adapt_pr
from ml.pipelines.replay.manus import is_manus_lane

class ReplayTest(unittest.TestCase):
    def test_adapt(self) -> None:
        pr = adapt_pr({"number": 1, "base": "master"})
        self.assertEqual(pr["base"]["ref"], "master")
    def test_manus(self) -> None:
        self.assertTrue(is_manus_lane(265))
        self.assertFalse(is_manus_lane(175))

if __name__ == "__main__":
    unittest.main()
