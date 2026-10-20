import json
import unittest
from pathlib import Path

from she.metrics.agent_throughput import (\n    reduce_events,\n    retry_amplification_ratio,\n    retry_recovery_rate,\n    wilson_proportion_interval,\n)


ROOT = Path(__file__).resolve().parents[1]


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
                "agent_id": "a",
                "event": "task_completed",
                "metrics": {"additions": 9, "deletions": 1, "files_changed": 1},
            },
            {"timestamp": "2026-09-14T10:01:00Z", "agent_id": "a", "event": "task_started"},
        ], sequential_baseline_sec=120)
        self.assertIsNotNone(metrics.wtcv_per_min)
        self.assertIsNotNone(metrics.ates)
        self.assertGreater(metrics.weighted_completion, 0)

    def test_missing_complexity_does_not_fabricate_weighted_metrics(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00Z", "agent_id": "a", "event": "task_completed", "complexity_score": 2},
            {"timestamp": "2026-09-14T10:01:00Z", "agent_id": "a", "event": "task_completed"},
        ], sequential_baseline_sec=120)
        self.assertIsNone(metrics.wtcv_per_min)
        self.assertIsNone(metrics.ates)

    def test_malformed_timestamp_does_not_abort_valid_duration(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00Z", "agent_id": "a", "event": "task_started"},
            {"timestamp": "not-a-timestamp", "agent_id": "a", "event": "handoff", "latency_ms": 10},
            {"timestamp": "2026-09-14T10:01:00Z", "agent_id": "a", "event": "task_completed", "complexity_score": 1},
        ])
        self.assertEqual(metrics.workflow_minutes, 1.0)
        self.assertEqual(metrics.completed_tasks, 1)

    def test_invalid_complexity_evidence_remains_unavailable(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00Z", "agent_id": "a", "event": "task_completed", "complexity_score": "unknown"},
            {"timestamp": "2026-09-14T10:01:00Z", "agent_id": "a", "event": "task_completed", "complexity_score": -1},
        ], sequential_baseline_sec=120)
        self.assertEqual(metrics.weighted_completion, 0)
        self.assertIsNone(metrics.wtcv_per_min)
        self.assertIsNone(metrics.ates)

    def test_offset_naive_timestamps_are_excluded(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00", "agent_id": "a", "event": "task_started"},
            {"timestamp": "2026-09-14T10:01:00Z", "agent_id": "a", "event": "task_completed", "complexity_score": 1},
        ])
        self.assertEqual(metrics.workflow_minutes, 0.0)

    def test_missing_agent_identity_does_not_fabricate_agent_count(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00Z", "event": "task_completed", "complexity_score": 2},
            {"timestamp": "2026-09-14T10:01:00Z", "event": "task_started"},
        ], sequential_baseline_sec=120)
        self.assertEqual(metrics.agents, 0)
        self.assertIsNone(metrics.parallel_yield)
        self.assertIsNone(metrics.ates)

    def test_missing_baseline_does_not_fabricate_ates(self):
        metrics = reduce_events([
            {"timestamp": "2026-09-14T10:00:00Z", "agent_id": "a", "event": "task_completed", "complexity_score": 2},
            {"timestamp": "2026-09-14T10:01:00Z", "agent_id": "a", "event": "task_completed", "complexity_score": 2},
        ])
        self.assertIsNone(metrics.parallel_yield)
        self.assertIsNone(metrics.ates)


    def test_evidence_quality_equation_helpers(self):
        from she.metrics.agent_throughput import (
            correlation_completeness,
            evidence_coverage_ratio,
            validated_outcome_rate,
            validation_coverage,
        )

        self.assertEqual(evidence_coverage_ratio(4, 5), 0.8)
        self.assertEqual(validated_outcome_rate(3, 4), 0.75)
        self.assertEqual(validation_coverage(4, 5), 0.8)
        self.assertEqual(correlation_completeness(9, 10), 0.9)

    def test_evidence_quality_equations_preserve_missing_denominators(self):
        from she.metrics.agent_throughput import (
            correlation_completeness,
            evidence_coverage_ratio,
            validated_outcome_rate,
            validation_coverage,
        )

        self.assertIsNone(evidence_coverage_ratio(0, None))
        self.assertIsNone(evidence_coverage_ratio(0, 0))
        self.assertIsNone(validated_outcome_rate(None, 4))
        self.assertIsNone(validation_coverage(0, 0))
        self.assertIsNone(correlation_completeness(2, None))

    def test_evidence_quality_equations_reject_impossible_counts(self):
        from she.metrics.agent_throughput import (
            correlation_completeness,
            evidence_coverage_ratio,
            validated_outcome_rate,
            validation_coverage,
        )

        for calculate in (
            lambda: evidence_coverage_ratio(-1, 2),
            lambda: validated_outcome_rate(3, 2),
            lambda: validation_coverage(1, -2),
            lambda: correlation_completeness(1, 0),
        ):
            with self.subTest(calculate=calculate):
                with self.assertRaises(ValueError):
                    calculate()


    def test_retry_amplification_counts_attempts_per_logical_operation(self):
        self.assertEqual(retry_amplification_ratio(10, 10), 1.0)
        self.assertEqual(retry_amplification_ratio(13, 10), 1.3)
        self.assertIsNone(retry_amplification_ratio(None, 10))
        self.assertIsNone(retry_amplification_ratio(0, 0))

    def test_retry_recovery_uses_logical_operation_denominator(self):
        self.assertEqual(retry_recovery_rate(6, 8), 0.75)
        self.assertIsNone(retry_recovery_rate(0, 0))
        self.assertIsNone(retry_recovery_rate(2, None))

    def test_wilson_interval_matches_wolfram_reference_fixtures(self):
        self.assertEqual(wilson_proportion_interval(3, 4), (0.300636, 0.954414))
        self.assertEqual(wilson_proportion_interval(75, 100), (0.656954, 0.824549))
        self.assertIsNone(wilson_proportion_interval(0, 0))
        self.assertIsNone(wilson_proportion_interval(1, None))

    def test_retry_and_interval_helpers_reject_invalid_inputs(self):
        invalid_calls = (
            lambda: retry_amplification_ratio(9, 10),
            lambda: retry_amplification_ratio(-1, 1),
            lambda: retry_recovery_rate(4, 3),
            lambda: wilson_proportion_interval(5, 4),
            lambda: wilson_proportion_interval(1, 2, z_score=0),
        )
        for calculate in invalid_calls:
            with self.subTest(calculate=calculate):
                with self.assertRaises(ValueError):
                    calculate()


class AgentThroughputSchemaTest(unittest.TestCase):
    """Protect the telemetry boundary against undeclared sensitive fields."""

    def test_schema_is_closed_and_forbidden_fields_are_not_allowlisted(self):
        schema = json.loads(
            (ROOT / "docs/ops/AGENT-THROUGHPUT-EVENT.schema.json").read_text(encoding="utf-8")
        )
        self.assertFalse(schema["additionalProperties"])
        properties = schema["properties"]
        self.assertIn("metrics", properties)
        for forbidden in ("prompt", "completion", "credentials", "tool_payload", "secret", "message_body"):
            self.assertNotIn(forbidden, properties)

    def test_structural_metrics_extension_is_closed(self):
        schema = json.loads(
            (ROOT / "docs/ops/AGENT-THROUGHPUT-EVENT.schema.json").read_text(encoding="utf-8")
        )
        metrics = schema["properties"]["metrics"]
        self.assertFalse(metrics["additionalProperties"])
        self.assertEqual(
            set(metrics["properties"]),
            {"additions", "deletions", "files_changed", "complexity_score"},
        )


if __name__ == "__main__":
    unittest.main()
