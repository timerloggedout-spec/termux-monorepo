"""Quota dispatch drift guard.

Statically enforces the Tier 0 takeover invariants from issue #1573:

1. Every lane named in the quota-dispatch-tree.yml matrix exists as a
   workflow file and declares a workflow_dispatch trigger (no orphan or
   undispatchable entries).
2. No dispatcher-managed lane carries a schedule trigger (drift back to
   per-lane crons fails CI).
3. The dispatcher itself owns exactly one cron entry point.

Read-only: no network access, no provider calls. Run from the repository root.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
DISPATCHER = WORKFLOWS_DIR / "quota-dispatch-tree.yml"

MATRIX_LANE_RE = re.compile(r"^\s+- lane:\s*([A-Za-z0-9][A-Za-z0-9-]*)\s*$", re.MULTILINE)
SCHEDULE_TRIGGER_RE = re.compile(r"^\s{2}schedule:\s*$", re.MULTILINE)
WORKFLOW_DISPATCH_RE = re.compile(r"^\s{2}workflow_dispatch:\s*$", re.MULTILINE)
CRON_RE = re.compile(r"-\s*cron:\s*['\"]")


class QuotaDispatchDriftGuard(unittest.TestCase):
    def dispatcher_text(self):
        self.assertTrue(DISPATCHER.is_file(), "quota-dispatch-tree.yml is missing")
        return DISPATCHER.read_text(encoding="utf-8")

    def test_dispatcher_has_exactly_one_cron_entry_point(self):
        text = self.dispatcher_text()
        crons = CRON_RE.findall(text)
        self.assertEqual(len(crons), 1, "quota-dispatch-tree must own exactly one cron")

    def test_matrix_lanes_exist_and_are_dispatchable(self):
        text = self.dispatcher_text()
        lanes = MATRIX_LANE_RE.findall(text)
        self.assertTrue(lanes, "dispatcher matrix has no lanes")
        for lane in lanes:
            with self.subTest(lane=lane):
                path = WORKFLOWS_DIR / f"{lane}.yml"
                self.assertTrue(path.is_file(), f"matrix lane {lane}.yml does not exist")
                lane_text = path.read_text(encoding="utf-8")
                self.assertIsNotNone(
                    WORKFLOW_DISPATCH_RE.search(lane_text),
                    f"matrix lane {lane}.yml has no workflow_dispatch trigger",
                )

    def test_matrix_lanes_carry_no_schedule_trigger(self):
        text = self.dispatcher_text()
        lanes = MATRIX_LANE_RE.findall(text)
        for lane in lanes:
            with self.subTest(lane=lane):
                path = WORKFLOWS_DIR / f"{lane}.yml"
                if not path.is_file():
                    continue  # covered by test_matrix_lanes_exist_and_are_dispatchable
                lane_text = path.read_text(encoding="utf-8")
                self.assertIsNone(
                    SCHEDULE_TRIGGER_RE.search(lane_text),
                    f"dispatched lane {lane}.yml re-added a schedule trigger "
                    "(drift from issue #1573; move the cadence into a dispatcher node)",
                )


if __name__ == "__main__":
    unittest.main()
