import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

CAT = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/grok-build.yaml"


class GrokBuildCatalogTests(unittest.TestCase):
    def test_observe_only(self):
        doc = load_simple_yaml(CAT)
        self.assertEqual(doc["id"], "grok-build")
        self.assertTrue(doc["observe_only"])


if __name__ == "__main__":
    unittest.main()
