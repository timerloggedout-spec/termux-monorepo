import unittest

from she.metrics.agent_throughput import reduce_events


class AgentThroughputTest(unittest.TestCase):
    """Lock the observational ATES contract to small, auditable fixtures."""

    def test_quality_weighted_observational_metrics(self):
        events = [
            {"timestamp": "2026-09-14T10:00:00Z", "agent_id": "a", "event": "task_started", "task_id": "t1"},
            {"timestamp": "2026-09-14T10:00:02Z", "agent_id": "a", "event": "tool_call", "tool": "git", "status": "success", "duration_ms": 100},
            {"timestamp": "2026-09-14T10:00:03Z", "agent_id": "b", "event": "handoff", "latency_ms": 500},
            {"timestamp": "2026-09-14T10:00:04Z", "agent_id": "b", "event": "tool_call", "tool": "test", "status": "failed", "duration_ms": 200},
            {"timestamp": "2026-09-14T10:00:05Z", "agent_id": "b", "event": "tool_retry", "tool": "test"},
            {"timestamp": "2026-09-14T10:00:10Z", "agent_id": "b", "event": "task_completed", "task_id": "t1", "complexity_score": 3.0},
        ]
        metrics = reduce_events(events, sequential_baseline_sec=20)
        self.assertEqual(metrics.completed_tasks, 1)
        self.assertEqual(metrics.weighted_completion, 3.0)
        self.assertEqual(metrics.tool_actions, 3)
        self.assertEqual(metrics.failed_actions, 1)
        self.assertEqual(metrics.retries, 1)
        self.assertEqual(metrics.agents, 2)
        self.assertIsNotNone(metrics.ates)
        self.assertGreater(metrics.wtcv_per_min, metrics.tcv_tasks_per_min)
        self.assertEqual(metrics.mean_handoff_latency_ms, 500.0)

    def test_structural_complexity_fallback_is_supported(self):
        metrics = reduce_events([
            {
                "timestamp": "2026-09-14T10:00:00Z",
                "event": "task_completed",
                "metrics": {"additions": 9, "deletions": 1, "files_changed": 1},
            },
            {"timestamp": "2026-09-14T10:01:00Z", "event": "task_started"},
        ], sequential_baseline_sec=120)
        self.assertIsNotNone(metrics.wtcv_per_min)
        self.assertIsNotNone(metrics.ates)
        self.assertGreater(metrics.weighted_completion, 0)

    def test_missing_complexity_does_not_fabricate_weighted_metrics(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00Z", "event": "task_completed", "complexity_score": 2},
            {"timestamp": "2026-09-14T10:01:00Z", "event": "task_completed"},
        ], sequential_baseline_sec=120)
        self.assertIsNone(metrics.wtcv_per_min)
        self.assertIsNone(metrics.ates)

    def test_missing_baseline_does_not_fabricate_ates(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00Z", "event": "task_completed", "complexity_score": 2},
            {"timestamp": "2026-09-14T10:01:00Z", "event": "task_completed", "complexity_score": 2},
        ])
        self.assertIsNone(metrics.parallel_yield)
        self.assertIsNone(metrics.ates)


if __name__ == "__main__":
    unittest.main()
