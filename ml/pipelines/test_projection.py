import unittest
from ml.pipelines.viz.projection import project

class ProjectionTest(unittest.TestCase):
    def test_counts(self) -> None:
        out = project({"master_sha": "abc1234", "session": "t"}, [{"lane": "EXTRACT", "number": 1}])
        self.assertEqual(out["lanes"]["EXTRACT"], 1)

if __name__ == "__main__":
    unittest.main()
