"""Registry fixture tests."""
from __future__ import annotations

import unittest
from pathlib import Path

from ml.pipelines.lib.io import load_json


class TestRegistry(unittest.TestCase):
    def test_fixture_has_issue_175(self) -> None:
        payload = load_json(Path(__file__).resolve().parents[1] / "fixtures" / "session_20260920.json")
        self.assertEqual(payload["issue"], 175)
        self.assertGreaterEqual(len(payload["prs"]), 5)


if __name__ == "__main__":
    unittest.main()
