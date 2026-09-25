import tempfile
import unittest
from pathlib import Path

from foresight.registry import append, fingerprint, load, validate


class ForesightRegistryTests(unittest.TestCase):
    def record(self):
        return {
            "resource_id": "test-1",
            "title": "Test resource",
            "category": "testing",
            "horizon": "H0",
            "evidence_status": "confirmed",
            "summary": "A deterministic test record.",
            "source": {"url": "https://example.org/source"},
            "observed_at": "2026-09-25T00:00:00+00:00",
            "confidence": 0.95,
            "procurement": {"horizon": "H0", "decision_status": "watch"}
        }

    def test_append_validate_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "resource-registry.jsonl"
            record = append(path, self.record())
            self.assertEqual(validate(record), [])
            self.assertEqual(record["evidence_hash"], fingerprint(record))
            self.assertEqual(len(load(path)), 1)

    def test_invalid_horizon(self):
        record = self.record()
        record["horizon"] = "H9"
        self.assertTrue(validate(record))

    def test_hash_changes_when_record_changes(self):
        a = self.record()
        b = dict(a)
        b["summary"] = "changed"
        self.assertNotEqual(fingerprint(a), fingerprint(b))


if __name__ == "__main__":
    unittest.main()
