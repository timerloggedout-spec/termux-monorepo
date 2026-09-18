import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/gemini.yaml"


class ProviderGeminiTests(unittest.TestCase):
    def test_catalog(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "gemini")
        self.assertEqual(doc["issue"], 272)
        self.assertEqual(doc["class"], "agent-lane")
        self.assertTrue(doc["observe_only"])
        self.assertIn("gemini-dispatch", str(doc.get("surface")))


if __name__ == "__main__":
    unittest.main()
