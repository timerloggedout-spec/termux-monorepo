import unittest
from ml.pipelines.peers.collision import collisions_among
from ml.pipelines.peers.jules import is_jules
from ml.pipelines.peers.overlap import title_overlap

class CollisionTest(unittest.TestCase):
    def test_overlap(self) -> None:
        prs = [
            {"number": 1, "files": ["a.py", "b.py"]},
            {"number": 2, "files": ["b.py", "c.py"]},
        ]
        hits = collisions_among(prs)
        self.assertEqual(hits[0][2], ["b.py"])
    def test_jules_and_palette(self) -> None:
        self.assertTrue(is_jules({"user": {"login": "google-labs-jules[bot]"}}))
        self.assertTrue(title_overlap("Palette: heartbeat"))
