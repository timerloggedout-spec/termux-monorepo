import unittest
from ml.pipelines.features.docs_only import flag

class FeatureFlagTests(unittest.TestCase):
    def test_true(self) -> None:
        key = {
            "staleness": "stale_base",
            "security": "security",
            "docs_only": "docs_only",
            "bot_authors": "author",
        }["docs_only"]
        sample = {key: True} if key != "author" else {"author": "google-labs-jules[bot]"}
        self.assertTrue(flag(sample))

    def test_false(self) -> None:
        self.assertFalse(flag({}))
