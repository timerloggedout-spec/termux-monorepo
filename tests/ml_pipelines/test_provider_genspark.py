import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/genspark.yaml"


class ProviderGensparkTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "genspark")
        self.assertEqual(doc["issue"], 364)
        self.assertEqual(doc["class"], "provider-attribution")
        self.assertTrue(doc["observe_only"])
        self.assertIn("proposal", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
