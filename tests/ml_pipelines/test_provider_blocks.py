import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

CAT = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/blocks.yaml"


class BlocksCatalogTests(unittest.TestCase):
    def test_observe_only(self):
        doc = load_simple_yaml(CAT)
        self.assertEqual(doc["id"], "blocks")
        self.assertIn("reviewer_noise", str(doc.get("activity_taxonomy") or ""))


if __name__ == "__main__":
    unittest.main()
