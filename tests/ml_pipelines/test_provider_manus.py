import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/manus.yaml"


class ProviderManusTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "manus")
        self.assertEqual(doc["issue"], 358)
        self.assertEqual(doc["class"], "provider-attribution")
        self.assertTrue(doc["observe_only"])
        self.assertIn("computer-replay", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
