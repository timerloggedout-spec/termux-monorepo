import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/mistral.yaml"


class ProviderMistralTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "mistral")
        self.assertEqual(doc["issue"], 361)
        self.assertEqual(doc["class"], "provider-attribution")
        self.assertTrue(doc["observe_only"])
        self.assertIn("proposal", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
