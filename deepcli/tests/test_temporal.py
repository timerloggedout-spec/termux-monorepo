"""Temporal assignment-window and collector-cycle regressions."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deepcli.observatory.temporal import AssignmentWindow, CollectorCycle, Phase, QueObservation, TemporalError, classify_assignment, classify_que_event, next_collector_ticks, plan_wait
UTC = timezone.utc
BASE = datetime(2026, 11, 27, 12, 0, tzinfo=UTC)

class TemporalTests(unittest.TestCase):
    def setUp(self):
        self.window = AssignmentWindow(BASE, BASE-timedelta(seconds=30), BASE+timedelta(minutes=5), timedelta(minutes=2))
    def test_early_phase_inside_window(self):
        result = classify_assignment(self.window, BASE-timedelta(seconds=10))
        self.assertEqual(result.phase, Phase.EARLY)
        self.assertFalse(result.window_expired)
    def test_late_phase_inside_window(self):
        result = classify_assignment(self.window, BASE+timedelta(minutes=1))
        self.assertEqual(result.phase, Phase.LATE)
        self.assertFalse(result.window_expired)
    def test_window_expiry_and_duration_overrun_are_independent(self):
        result = classify_assignment(self.window, BASE+timedelta(minutes=6), BASE+timedelta(minutes=9))
        self.assertEqual(result.phase, Phase.WINDOW_EXPIRED)
        self.assertTrue(result.window_expired)
        self.assertTrue(result.duration_overrun)
    def test_duration_overrun_inside_window(self):
        result = classify_assignment(self.window, BASE, BASE+timedelta(minutes=3))
        self.assertEqual(result.phase, Phase.ON_BEAT)
        self.assertTrue(result.duration_overrun)
        self.assertFalse(result.window_expired)
    def test_wait_selects_earliest_boundary(self):
        plan = plan_wait(BASE, expected_completion=BASE+timedelta(minutes=2), window_close=BASE+timedelta(minutes=5), max_wait_until=BASE+timedelta(minutes=4))
        self.assertEqual(plan.wake_at, BASE+timedelta(minutes=2))
        self.assertEqual(plan.reason, "expected_completion")
    def test_event_wakes_immediately(self):
        plan = plan_wait(BASE, window_close=BASE+timedelta(minutes=5), event_ready=True)
        self.assertEqual((plan.wake_at, plan.reason), (BASE, "event"))
    def test_independent_collector_phases(self):
        cycles = [CollectorCycle(BASE, timedelta(seconds=10), timedelta(seconds=2)), CollectorCycle(BASE, timedelta(seconds=7), timedelta(seconds=3))]
        self.assertEqual(next_collector_ticks(cycles, BASE), (BASE+timedelta(seconds=2), BASE+timedelta(seconds=3)))
    def test_que_completion_remains_observation(self):
        self.assertEqual(classify_que_event("completed"), QueObservation.COMPLETED_OBSERVED)
        self.assertEqual(classify_que_event("vanished"), QueObservation.RECONCILE_MISSING)
    def test_naive_timestamp_rejected(self):
        with self.assertRaises(TemporalError):
            classify_assignment(self.window, datetime(2026, 11, 27, 12, 0))

if __name__ == "__main__":
    unittest.main()
