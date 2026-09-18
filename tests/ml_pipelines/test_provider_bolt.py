import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/bolt.yaml"


class ProviderBoltTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "bolt")
        self.assertEqual(doc["issue"], 187)
        self.assertEqual(doc["class"], "specialist-lane")
        self.assertTrue(doc["observe_only"])
        self.assertIn("perf/ast-grep", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
