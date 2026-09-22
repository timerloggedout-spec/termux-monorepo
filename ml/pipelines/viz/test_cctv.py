import unittest
from ml.pipelines.viz.cctv import cctv

class CctvTests(unittest.TestCase):
    def test_counts(self) -> None:
        view = cctv([{"lane": "hold"}, {"lane": "hold"}, {"lane": "wait"}])
        self.assertEqual(view["n"], 3)
        self.assertEqual(view["lanes"]["hold"], 2)
        self.assertEqual(view["step"], 10023)
