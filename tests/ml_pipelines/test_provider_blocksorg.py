import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

PATH = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers/blocksorg.yaml"


class ProviderTests(unittest.TestCase):
    def test_observe_only(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc["id"], "blocksorg")
        self.assertTrue(doc["observe_only"])
        self.assertFalse(doc["may_write_master"])


if __name__ == "__main__":
    unittest.main()
