"""Temporal assignment-window and collector-cycle regressions."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
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
    def test_window_close_is_inclusive(self):
        result = classify_assignment(self.window, self.window.closes_at)
        self.assertEqual(result.phase, Phase.LATE)
        self.assertFalse(result.window_expired)

    def test_dst_fold_uses_elapsed_utc_time(self):
        zone = ZoneInfo("America/New_York")
        first_0130 = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=0)
        second_0130 = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
        cycle = CollectorCycle(first_0130, timedelta(minutes=15))
        next_tick = cycle.next_tick_after(second_0130)
        self.assertEqual(next_tick.astimezone(UTC) - second_0130.astimezone(UTC), timedelta(minutes=15))

    def test_dst_window_order_and_length_use_elapsed_time(self):
        zone = ZoneInfo("America/New_York")
        opens = datetime(2026, 11, 1, 1, 15, tzinfo=zone, fold=0)
        nominal = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
        closes = datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=1)
        window = AssignmentWindow(nominal, opens, closes, timedelta(minutes=2))
        self.assertEqual(window.open_length, timedelta(minutes=90))
        first_0145 = datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=0)
        self.assertEqual(classify_assignment(window, first_0145).phase, Phase.EARLY)

    def test_dst_wait_ignores_past_wall_clock_deadline(self):
        zone = ZoneInfo("America/New_York")
        now = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
        past = datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=0)
        future = datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=1)
        plan = plan_wait(now, expected_completion=future, window_close=past)
        self.assertEqual(plan.reason, "window_close")
        self.assertEqual(plan.wake_at, now.astimezone(UTC))

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(TemporalError):
            classify_assignment(self.window, datetime(2026, 11, 27, 12, 0))

if __name__ == "__main__":
    unittest.main()
