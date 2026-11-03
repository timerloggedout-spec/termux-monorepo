"""Deterministic tests for the isolated visualization research lane."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.visualization_lab.validate_cohort import validate as validate_cohort
from scripts.visualization_lab.validate_dashboard_snapshot import inspect_snapshot


class CohortContractTests(unittest.TestCase):
    def test_fixture_is_valid_and_synthetic(self):
        root = Path(__file__).resolve().parents[1]
        fixture = root / "experiments/visualization-renderers/fixtures/renderer-cohort-v1.json"
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(payload["data_class"], "synthetic")
        self.assertEqual(validate_cohort(payload), [])

    def test_unknown_network_endpoint_is_rejected(self):
        payload = {
            "schema": "renderer-cohort/v1", "data_class": "synthetic",
            "fixture_id": "invalid", "hierarchy": {"id": "root"},
            "network": {
                "nodes": [{"id": "a"}],
                "edges": [{"id": "e", "source": "a", "target": "missing"}],
            },
            "series": {"unit": "count", "generated_at": "2026-11-02T00:00:00Z",
                       "points": [{"t": "2026-11-01T00:00:00Z", "value": 1},
                                  {"t": "2026-11-02T00:00:00Z", "value": None}]},
        }
        self.assertTrue(any("unknown endpoint" in item for item in validate_cohort(payload)))


class SnapshotContractTests(unittest.TestCase):
    def _write(self, folder, name, value):
        path = Path(folder) / name
        path.write_text(value, encoding="utf-8")
        return path

    def test_empty_snapshot_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            report = inspect_snapshot(self._write(folder, "empty.json", "  "))
        self.assertEqual(report["state"], "invalid")
        self.assertIn("snapshot is empty", report["errors"][0])

    def test_malformed_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            report = inspect_snapshot(self._write(folder, "bad.json", "{"))
        self.assertEqual(report["state"], "invalid")

    def test_missing_or_naive_timestamp_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = inspect_snapshot(self._write(folder, "missing.json", '{"items":[]}'))
            naive = inspect_snapshot(self._write(folder, "naive.json",
                '{"generated_at":"2026-11-02T00:00:00","items":[]}'))
        self.assertEqual(missing["state"], "invalid")
        self.assertEqual(naive["state"], "invalid")

    def test_stale_is_distinct_from_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self._write(folder, "stale.json",
                '{"schema":"feed/v1","generated_at":"2026-10-30T00:00:00Z"}')
            report = inspect_snapshot(path, now=datetime(2026, 11, 2, tzinfo=timezone.utc))
        self.assertEqual(report["state"], "valid")
        self.assertTrue(any("stale" in warning for warning in report["warnings"]))

    def test_fresh_timestamped_snapshot_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self._write(folder, "fresh.json",
                '{"schema":"feed/v1","generated_at":"2026-11-02T00:00:00Z"}')
            report = inspect_snapshot(path, now=datetime(2026, 11, 2, 1, tzinfo=timezone.utc))
        self.assertEqual(report["state"], "valid")
        self.assertEqual(report["warnings"], [])


if __name__ == "__main__":
    unittest.main()
