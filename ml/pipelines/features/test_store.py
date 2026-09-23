"""Feature store tests."""
from __future__ import annotations

import unittest

from ml.pipelines.features.store import FeatureStore


class TestStore(unittest.TestCase):
    def test_upsert_merges(self) -> None:
        store = FeatureStore()
        store.upsert(679, {"security_fix": 1.0})
        store.upsert(679, {"tests_present": 1.0})
        self.assertEqual(store.get(679)["security_fix"], 1.0)
        self.assertEqual(store.get(679)["tests_present"], 1.0)


if __name__ == "__main__":
    unittest.main()
