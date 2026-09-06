import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/grok.yaml"


class ProviderGrokTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "grok")
        self.assertEqual(doc["issue"], 175)
        self.assertEqual(doc["class"], "operator-matrix")
        self.assertTrue(doc["observe_only"])
        self.assertIn("Administrator", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
