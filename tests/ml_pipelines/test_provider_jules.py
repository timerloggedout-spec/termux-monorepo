import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/jules.yaml"


class ProviderJulesTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "jules")
        self.assertEqual(doc["issue"], 337)
        self.assertEqual(doc["class"], "agent-lane")
        self.assertTrue(doc["observe_only"])
        self.assertIn("google-labs-jules[bot]", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
