import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/coderabbit.yaml"


class ProviderCoderabbitTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "coderabbit")
        self.assertEqual(doc["issue"], 192)
        self.assertEqual(doc["class"], "review-provider")
        self.assertTrue(doc["observe_only"])
        self.assertIn("@coderabbitai", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
