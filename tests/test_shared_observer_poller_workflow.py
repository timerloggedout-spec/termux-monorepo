from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "shared-observer-poller.yml"


class SharedObserverPollerWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_api_query_filters_to_recent_runs_before_pagination(self) -> None:
        self.assertIn("created=%3E%3D${SINCE}", self.workflow)
        self.assertIn("&per_page=100", self.workflow)
        self.assertNotIn("&per_page=50", self.workflow)
        self.assertIn("date -u -d '30 minutes ago'", self.workflow)
        self.assertIn("(now - 1800 | todate)", self.workflow)

    def test_observer_is_read_only_and_does_not_checkout_unused_sources(self) -> None:
        self.assertIn("actions: read", self.workflow)
        self.assertNotIn("contents: read", self.workflow)
        self.assertNotIn("issues: write", self.workflow)
        self.assertNotIn("actions/checkout", self.workflow)
        self.assertIn("timeout-minutes: 5", self.workflow)


if __name__ == "__main__":
    unittest.main()
