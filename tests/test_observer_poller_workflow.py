from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "observer-poller-scheduled.yml"


class ObserverPollerWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_run_query_is_bounded_before_pagination(self) -> None:
        self.assertIn("created=%3E%3D${CREATED_SINCE}", self.workflow)
        self.assertIn("&per_page=100", self.workflow)
        self.assertNotIn("&per_page=10", self.workflow)
        self.assertIn("CREATED_LOOKBACK=$((LOOKBACK + 1440))", self.workflow)

    def test_updated_at_filter_remains_the_emission_boundary(self) -> None:
        self.assertIn('.updated_at > "', self.workflow)
        self.assertIn("status=completed", self.workflow)
        self.assertIn('.conclusion == "success"', self.workflow)

    def test_manual_lookback_is_validated_before_shell_arithmetic(self) -> None:
        self.assertIn('[[ "${LOOKBACK}" =~ ^[0-9]+$ ]]', self.workflow)
        self.assertIn("LOOKBACK < 1 || LOOKBACK > 1440", self.workflow)
        self.assertIn("LOOKBACK=30", self.workflow)


if __name__ == "__main__":
    unittest.main()
