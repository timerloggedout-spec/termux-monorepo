import unittest
from ml.pipelines.ates.observer import observe
from ml.pipelines.ates.spine import SPINE

class AtesTest(unittest.TestCase):
    def test_observe(self) -> None:
        out = observe({"master_sha": "a3423d97"})
        self.assertEqual(out["issue"], 175)
        self.assertEqual(SPINE, "runtime-evidence")

if __name__ == "__main__":
    unittest.main()
