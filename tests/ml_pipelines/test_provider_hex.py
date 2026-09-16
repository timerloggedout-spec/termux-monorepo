import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

CAT = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/hex.yaml"


class HexCatalogTests(unittest.TestCase):
    def test_observe_only(self):
        doc = load_simple_yaml(CAT)
        self.assertTrue(doc["observe_only"])
        self.assertFalse(doc["may_write_master"])
        self.assertEqual(doc["id"], "hex")


if __name__ == "__main__":
    unittest.main()
