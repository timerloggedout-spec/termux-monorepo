"""Offline tests for the unified Integration Intelligence batch adapter."""
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
OPS = ROOT / "scripts" / "ops"
sys.path.insert(0, str(OPS))
spec = importlib.util.spec_from_file_location("integration_event", OPS / "integration_event.py")
ie = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ie)

EVENT = {
    "schema_version": "1.0.0",
    "event_id": "evt-001",
    "integration_id": "github-actions",
    "event_type": "workflow_run.completed",
    "source": {"repository": "timerloggedout-spec/termux-monorepo", "workflow_run_id": 42},
    "execution": {"status": "succeeded", "started_at": "2026-11-14T12:00:00Z",
                  "completed_at": "2026-11-14T12:00:01Z", "duration_ms": 1000},
    "outcome": {"state": "validated", "summary": "checks completed", "confidence": "high"},
    "evidence": {"artifact_refs": [], "validation_status": "passed"},
    "provenance": {"provider": "github", "capture_method": "workflow_run", "attribution": "provider_reported"},
    "idempotency_key": "github:run:42:attempt:1",
}

MEASUREMENT = {
    "schema_version": "1.0.0",
    "measurement_id": "m-001",
    "event_id": "evt-001",
    "integration_id": "github-actions",
    "metric_name": "workflow.duration_ms",
    "metric_type": "duration",
    "value": 1000,
    "unit": "ms",
    "temporality": "instant",
    "measurement_status": "measured",
    "observed_at": "2026-11-14T12:00:02Z",
    "dimensions": {"workflow": "repo-gate", "conclusion": "success"},
    "provenance": {"provider": "github", "capture_method": "workflow_run", "attribution": "provider_reported"},
    "idempotency_key": "github:run:42:duration",
}


class IntegrationEventBatchTests(unittest.TestCase):
    def test_v1_event_is_accepted_without_observed_at(self):
        self.assertEqual(ie.validate_event(dict(EVENT))["schema_version"], "1.0.0")

    def test_manual_validator_matches_published_contract_keys(self):
        event_schema = json.loads((ROOT / "docs/integrations/schemas/integration-event.schema.json").read_text())
        measurement_schema = json.loads((ROOT / "docs/integrations/schemas/integration-measurement.schema.json").read_text())
        self.assertEqual(set(event_schema["properties"]), ie.EVENT_ALLOWED)
        self.assertEqual(set(event_schema["required"]), ie.EVENT_REQUIRED)
        self.assertEqual(set(measurement_schema["properties"]), ie.MEASUREMENT_ALLOWED)
        self.assertEqual(set(measurement_schema["required"]), ie.MEASUREMENT_REQUIRED)
        self.assertFalse(event_schema["additionalProperties"])
        self.assertFalse(measurement_schema["additionalProperties"])

    def test_v10_rejects_v11_timestamp_fields(self):
        event = dict(EVENT, observed_at="2026-11-14T12:00:02Z")
        with self.assertRaisesRegex(ValueError, "require schema_version 1.1.0"):
            ie.validate_event(event)

    def test_v11_requires_observed_at_and_privacy_classification(self):
        event = dict(EVENT, schema_version="1.1.0", observed_at="2026-11-14T12:00:02Z",
                     privacy={"classification": "internal", "contains_raw_prompt": False,
                              "contains_secret": False, "redaction_applied": True})
        self.assertEqual(ie.validate_event(event)["schema_version"], "1.1.0")
        del event["observed_at"]
        with self.assertRaisesRegex(ValueError, "observed_at"):
            ie.validate_event(event)
        event["observed_at"] = "2026-11-14T12:00:02Z"
        del event["privacy"]["classification"]
        with self.assertRaisesRegex(ValueError, "classification"):
            ie.validate_event(event)

    def test_unknown_fields_fail_closed(self):
        event = dict(EVENT, unexpected="value")
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            ie.validate_event(event)

    def test_raw_prompt_and_secret_flags_are_rejected(self):
        event = dict(EVENT, privacy={"classification": "internal", "contains_raw_prompt": True})
        with self.assertRaisesRegex(ValueError, "raw prompts or secrets"):
            ie.validate_event(event)

    def test_secret_shaped_value_is_rejected(self):
        event = dict(EVENT)
        event["outcome"] = {"state": "failed", "summary": "token ghp_abcdefghijklmnopqrstuvwxyz123456"}
        with self.assertRaisesRegex(ValueError, "secret-shaped"):
            ie.validate_event(event)

    def test_measurement_allows_tokenizer_and_token_count_dimensions(self):
        record = dict(MEASUREMENT, dimensions={"tokenizer": "o200k_base", "input_tokens": 128})
        self.assertEqual(ie.validate_measurement(record)["dimensions"]["input_tokens"], 128)

    def test_measurement_rejects_provider_token_dimension(self):
        for key in ("provider_token", "aws_secret_access_key"):
            record = dict(MEASUREMENT, dimensions={key: "opaque-value"})
            with self.assertRaisesRegex(ValueError, "sensitive field rejected"):
                ie.validate_measurement(record)

    def test_sql_literal_handles_null_cursor(self):
        self.assertEqual(ie.sql_literal(None), "NULL")
        sql, _ = ie.build_batch_sql([dict(EVENT)], "event", str(uuid.uuid4()))
        self.assertIn("NULL,\n  NULL,", sql)

    def test_insert_select_conflict_clause_is_disambiguated(self):
        for record, kind in ((dict(EVENT), "event"), (dict(MEASUREMENT), "measurement")):
            sql, _ = ie.build_batch_sql([record], kind, str(uuid.uuid4()))
            self.assertIn("FROM _integration_batch_docs\n  WHERE true\n  ON CONFLICT", sql)

    def test_cursor_guard_uses_non_input_dollar_quote_tag(self):
        sql, _ = ie.build_batch_sql([dict(MEASUREMENT)], "measurement", str(uuid.uuid4()),
                                    cursor_before="before", cursor_after="after$cursor_guard$; SELECT 1; --")
        self.assertIn("DO $cursor_guard_", sql)
        self.assertIn("integration_cursor_conflict", sql)

    def test_measurement_accepts_finite_numeric_point(self):
        self.assertEqual(ie.validate_measurement(dict(MEASUREMENT))["value"], 1000)

    def test_missing_measurement_is_null_not_zero(self):
        record = dict(MEASUREMENT, value=None, measurement_status="not_established")
        self.assertIsNone(ie.validate_measurement(record)["value"])

    def test_unestablished_measurement_cannot_have_value(self):
        record = dict(MEASUREMENT, measurement_status="not_established", value=0)
        with self.assertRaisesRegex(ValueError, "must have null value"):
            ie.validate_measurement(record)

    def test_measured_measurement_requires_a_value(self):
        record = dict(MEASUREMENT, measurement_status="measured", value=None)
        with self.assertRaisesRegex(ValueError, "require a numeric value"):
            ie.validate_measurement(record)

    def test_non_finite_measurement_is_rejected(self):
        record = dict(MEASUREMENT, value=float("nan"))
        with self.assertRaisesRegex(ValueError, "finite number"):
            ie.validate_measurement(record)

    def test_batching_respects_record_limit(self):
        records = [dict(MEASUREMENT, measurement_id=f"m-{i}", idempotency_key=f"key-{i}") for i in range(3)]
        chunks = ie.chunk_records(records, max_records=2, max_bytes=ie.HARD_MAX_BYTES)
        self.assertEqual([len(chunk) for chunk in chunks], [2, 1])

    def test_batching_respects_byte_limit_and_rejects_oversize(self):
        records = [dict(MEASUREMENT, measurement_id="m-big", idempotency_key="big")]
        with self.assertRaisesRegex(ValueError, "exceeds max batch bytes"):
            ie.chunk_records(records, max_records=2, max_bytes=100)

    def test_batch_groups_never_mix_integrations(self):
        a = dict(MEASUREMENT)
        b = dict(MEASUREMENT, measurement_id="m-2", idempotency_key="k-2", integration_id="other-source")
        groups = ie.group_by_integration([a, b])
        self.assertEqual(list(groups), ["github-actions", "other-source"])

    def test_sql_escapes_untrusted_string_literals(self):
        event = dict(EVENT, event_id="x'; DROP TABLE integration_events; --",
                     idempotency_key="key'; SELECT pg_sleep(99); --")
        ie.validate_event(event)
        sql, meta = ie.build_batch_sql([event], "event", str(uuid.uuid4()))
        self.assertIn("x''; DROP TABLE integration_events; --", sql)
        self.assertIn("ON CONFLICT (idempotency_key) DO NOTHING", sql)
        self.assertEqual(meta["records_received"], 1)

    def test_batch_sql_records_receipt_and_cursors_in_same_transaction(self):
        sql, meta = ie.build_batch_sql(
            [dict(MEASUREMENT)], "measurement", str(uuid.uuid4()),
            cursor_before="page-004", cursor_after="page-005",
        )
        self.assertTrue(sql.startswith("SET standard_conforming_strings = on;\nBEGIN;"))
        self.assertIn("INSERT INTO integration_measurements", sql)
        self.assertIn("INSERT INTO integration_ingest_batches", sql)
        self.assertIn("'page-004'", sql)
        self.assertIn("'page-005'", sql)
        self.assertIn("pg_advisory_xact_lock(hashtextextended(", sql)
        self.assertIn("FROM integration_latest_cursors", sql)
        self.assertIn("IS DISTINCT FROM 'page-004'", sql)
        self.assertIn("IS DISTINCT FROM 'page-005'", sql)
        self.assertIn("integration_cursor_conflict", sql)
        self.assertIn("COMMIT;", sql)
        self.assertEqual(meta["record_type"], "measurement")
        self.assertEqual(meta["cursor_after"], "page-005")

    def test_cursor_metadata_advances_only_on_final_batch(self):
        records = [
            dict(MEASUREMENT, measurement_id=f"m-{i}", idempotency_key=f"key-{i}")
            for i in range(3)
        ]
        cursors = {MEASUREMENT["integration_id"]: {"cursor_before": "page-004", "cursor_after": "page-005"}}
        batches = ie.plan(records, 2, ie.HARD_MAX_BYTES, cursors)[0]["batches"]
        self.assertEqual(batches[0]["cursor_before"], "page-004")
        self.assertNotIn("cursor_after", batches[0])
        self.assertNotIn("cursor_before", batches[1])
        self.assertEqual(batches[1]["cursor_after"], "page-005")
        with patch.object(ie, "run_batch", side_effect=lambda *args: {
            "cursor_before": args[4], "cursor_after": args[5]
        }) as run:
            ie.ingest("postgresql://writer", records, "measurement", 2, ie.HARD_MAX_BYTES,
                      cursor_metadata=cursors)
        self.assertEqual(run.call_args_list[0].args[4:], ("page-004", None))
        # The final checkpoint transaction must compare-and-swap against the
        # original stored cursor, even when earlier chunks have committed.
        self.assertEqual(run.call_args_list[1].args[4:], ("page-004", "page-005"))

    def test_cursor_guard_is_omitted_without_cursor_advance(self):
        sql, _ = ie.build_batch_sql([dict(MEASUREMENT)], "measurement", str(uuid.uuid4()),
                                    cursor_before="page-004")
        self.assertNotIn("pg_advisory_xact_lock", sql)
        self.assertNotIn("integration_cursor_conflict", sql)

    def test_batch_metadata_rejects_secret_shaped_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "batch.json"
            path.write_text(json.dumps({
                "event": {"github-actions": {"cursor_after": "ghp_abcdefghijklmnopqrstuvwxyz123456"}}
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "secret-shaped"):
                ie.load_batch_metadata(str(path))

    def test_dry_run_never_resolves_database_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "events.jsonl"
            path.write_text(json.dumps(EVENT) + "\n", encoding="utf-8")
            original = ie.resolve_writer_url
            ie.resolve_writer_url = lambda: (_ for _ in ()).throw(AssertionError("database must not be touched"))
            try:
                self.assertEqual(ie.main(["record", "--events-file", str(path), "--dry-run"]), 0)
            finally:
                ie.resolve_writer_url = original

    def test_failed_database_batch_writes_metadata_only_receipt(self):
        with patch.object(ie.lane_event, "psql", side_effect=[RuntimeError("connection detail"), ""]) as mocked:
            with self.assertRaisesRegex(RuntimeError, "connection detail"):
                ie.run_batch("postgresql://redacted", [dict(MEASUREMENT)], "measurement",
                             cursor_before="page-004", cursor_after="page-005")
        self.assertEqual(mocked.call_count, 2)
        failure_sql = mocked.call_args_list[1].args[1][1]
        self.assertIn("'failed'", failure_sql)
        self.assertIn("'RuntimeError'", failure_sql)
        self.assertNotIn("connection detail", failure_sql)
        self.assertIn("cursor_before", failure_sql)
        self.assertIn("'page-004'", failure_sql)
        self.assertIn("cursor_after", failure_sql)
        self.assertIn("NULL", failure_sql)
        self.assertNotIn("page-005", failure_sql)

    def test_legacy_database_url_is_never_used_as_writer_credential(self):
        with patch.dict(os.environ, {"LANE_EVENTS_DATABASE_URL": "postgresql://legacy-owner"}, clear=True):
            self.assertIsNone(ie.resolve_writer_url())

    def test_writer_role_resolution_requires_dedicated_role(self):
        with patch.dict(os.environ, {"NEON_API_KEY": "dummy"}, clear=True):
            with patch.object(ie.lane_event, "_neon", side_effect=[
                {"projects": [{"id": "project-1", "name": ie.lane_event.NEON_PROJECT}]},
                {"branches": [{"id": "branch-other", "default": False}], "pagination": {"next": "next-page"}},
                {"branches": [{"id": "branch-1", "default": True}], "pagination": {"next": None}},
                {"roles": [{"name": "neondb_owner"}, {"name": "integration_ingest"}]},
                {"uri": "postgresql://dedicated-writer"},
            ]) as neon:
                self.assertEqual(ie.resolve_writer_url(), "postgresql://dedicated-writer")
                self.assertIn("role_name=integration_ingest", neon.call_args_list[4].args[1])
                self.assertIn("cursor=next-page", neon.call_args_list[2].args[1])

    def test_owner_role_is_not_used_as_writer_fallback(self):
        with patch.dict(os.environ, {"NEON_API_KEY": "dummy"}, clear=True):
            with patch.object(ie.lane_event, "_neon", side_effect=[
                {"projects": [{"id": "project-1", "name": ie.lane_event.NEON_PROJECT}]},
                {"branches": [{"id": "branch-1", "default": True}]},
                {"roles": [{"name": "neondb_owner"}]},
            ]):
                with self.assertRaises(ie.BlockedError):
                    ie.resolve_writer_url()

    def test_migration_credential_is_separate_from_writer_credential(self):
        with patch.dict(os.environ, {"LANE_EVENTS_WRITER_DATABASE_URL": "postgresql://writer"}, clear=True):
            self.assertIsNone(ie.resolve_migration_url())
        with patch.dict(os.environ, {"LANE_EVENTS_MIGRATION_DATABASE_URL": "postgresql://migration"}, clear=True):
            self.assertEqual(ie.resolve_migration_url(), "postgresql://migration")

    def test_record_does_not_apply_schema_automatically(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "events.jsonl"
            path.write_text(json.dumps(EVENT) + "\n", encoding="utf-8")
            with patch.object(ie, "resolve_writer_url", return_value="postgresql://writer"), \
                 patch.object(ie, "ingest", return_value=[]), \
                 patch.object(ie.lane_event, "psql") as psql:
                self.assertEqual(ie.main(["record", "--events-file", str(path)]), 0)
            psql.assert_not_called()

    def test_empty_record_batch_cannot_advance_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "batch.json"
            path.write_text(json.dumps({
                "event": {"github-actions": {"cursor_after": "page-005"}}
            }), encoding="utf-8")
            self.assertEqual(ie.main(["record", "--batch-metadata-file", str(path)]), 1)

    def test_schema_command_requires_operator_migration_credential(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(ie.lane_event, "psql") as psql:
            self.assertEqual(ie.main(["schema"]), 2)
            psql.assert_not_called()

    def test_database_migration_is_append_only_and_indexed(self):
        ddl = (ROOT / "ops" / "lane-events" / "integration-events.sql").read_text(encoding="utf-8")
        for table in ("integration_events", "integration_measurements", "integration_ingest_batches"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", ddl)
            self.assertIn(f"ON {table}", ddl)
        self.assertIn("BEFORE UPDATE OR DELETE", ddl)
        self.assertIn("BEFORE TRUNCATE", ddl)
        self.assertIn("REFERENCES integration_ingest_batches(batch_id)", ddl)
        self.assertIn("FOREIGN KEY (event_id, integration_id)", ddl)
        self.assertIn("DEFERRABLE INITIALLY DEFERRED", ddl)
        self.assertIn("value NOT IN", ddl)
        self.assertIn("CREATE OR REPLACE VIEW integration_latest_cursors", ddl)
        self.assertIn("UNIQUE (integration_id, idempotency_key)", ddl)
        self.assertNotIn("idempotency_key      text NOT NULL UNIQUE", ddl)
        self.assertIn("integration_ingest_batches_cursor_latest_ix", ddl)
        self.assertIn("USING brin", ddl)
        self.assertIn("jsonb_path_ops", ddl)


if __name__ == "__main__":
    unittest.main()
