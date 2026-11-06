"""Regression tests for fail-closed telemetry source ingestion."""
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.dashboards.telemetry_feed import _read_json


class TelemetrySourceReadTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)

    def _read(self, folder, name, raw):
        path = Path(folder) / name
        path.write_text(raw, encoding="utf-8")
        gaps, sources = [], []
        with patch("scripts.dashboards.telemetry_feed.ROOT", Path(folder)):
            value = _read_json(name, gaps, sources, now=self.now)
        return value, gaps, sources[0]

    def test_empty_source_is_invalid_not_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "empty.json", "  ")
        self.assertIsNone(value)
        self.assertEqual(source["state"], "invalid")
        self.assertIn("empty", source["reason"])
        self.assertTrue(source["source_sha256"])

    def test_malformed_source_is_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "bad.json", "{")
        self.assertIsNone(value)
        self.assertEqual(source["state"], "invalid")

    def test_naive_timestamp_is_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "naive.json",
                '{"generated_at":"2026-11-02T10:00:00"}')
        self.assertIsNotNone(value)
        self.assertEqual(source["state"], "invalid")

    def test_stale_source_is_marked_stale(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "stale.json",
                '{"generated_at":"2026-10-30T00:00:00Z"}')
        self.assertEqual(source["state"], "stale")
        self.assertGreater(source["age_hours"], 24)

    def test_fresh_source_carries_sha_and_age(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "fresh.json",
                '{"generated_at":"2026-11-02T11:00:00Z"}')
        self.assertEqual(source["state"], "fresh")
        self.assertEqual(source["age_hours"], 1.0)
        self.assertEqual(len(source["source_sha256"]), 64)

    def test_missing_source_is_named(self):
        with tempfile.TemporaryDirectory() as folder:
            gaps, sources = [], []
            with patch("scripts.dashboards.telemetry_feed.ROOT", Path(folder)):
                value = _read_json("absent.json", gaps, sources, now=self.now)
        self.assertIsNone(value)
        self.assertEqual(sources[0]["state"], "missing")
        self.assertTrue(any("absent.json" in gap for gap in gaps))

    def test_future_timestamp_is_clock_skew(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "future.json",
                '{"generated_at":"2026-11-02T15:00:00Z"}')
        self.assertEqual(source["state"], "clock_skew")
        self.assertLess(source["age_hours"], -1)

    def test_missing_timestamp_is_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "unknown.json", '{"items":[]}')
        self.assertEqual(source["state"], "unknown")
        self.assertIsNotNone(value)

    def test_non_object_json_root_is_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            value, gaps, source = self._read(folder, "array.json", '[]')
        self.assertIsNone(value)
        self.assertEqual(source["state"], "invalid")


if __name__ == "__main__":
    unittest.main()
