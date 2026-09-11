import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/sentinel.yaml"


class ProviderSentinelTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "sentinel")
        self.assertEqual(doc["issue"], 186)
        self.assertEqual(doc["class"], "specialist-lane")
        self.assertTrue(doc["observe_only"])
        self.assertIn("symlink/chmod", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
