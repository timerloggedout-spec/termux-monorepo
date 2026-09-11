import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml

CAT = Path(__file__).resolve().parents[2] / "ml_pipelines/catalogs/providers"


class CatalogTests(unittest.TestCase):
    def test_all_observe_only(self):
        files = list(CAT.glob("*.yaml"))
        self.assertGreaterEqual(len(files), 20)
        for path in files:
            doc = load_simple_yaml(path)
            self.assertTrue(doc.get("observe_only"))
            self.assertFalse(doc.get("may_write_master"))
            self.assertIn("id", doc)
            self.assertIn("issue", doc)


if __name__ == "__main__":
    unittest.main()
