import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/ox-alpha.yaml"


class ProviderOxAlphaTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "ox-alpha")
        self.assertEqual(doc["issue"], 408)
        self.assertEqual(doc["class"], "implementation-lane")
        self.assertTrue(doc["observe_only"])
        self.assertIn("DeepSeek", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
