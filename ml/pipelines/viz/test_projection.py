import unittest
from ml.pipelines.viz.projection import project

class ProjectionTests(unittest.TestCase):
    def test_project(self) -> None:
        payload = project({"master_sha": "d10a7a54", "issue": 175}, [{"number": 724, "lane": "wait", "score": 1.2}])
        self.assertEqual(payload["rows"][0]["pr"], 724)
        self.assertEqual(payload["cctv"]["surface"], "icm-cctv")
