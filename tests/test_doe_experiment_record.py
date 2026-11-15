"""Regression tests for canonical DoE/MVT evidence emission."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.doe.experiment_record import build_record, validate_record, write_failure_envelope

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"docs/ops/corpus/EXPERIMENT.schema.json"
BASE="1"*40
CANDIDATE="2"*40

class ExperimentRecordTests(unittest.TestCase):
    def record(self, **overrides):
        values=dict(experiment_id="test-001",observed_at="2026-11-15T12:00:00Z",
            baseline_sha=BASE,candidate_sha=CANDIDATE,merge_base_sha="3"*40,
            suite="contract",baseline_exit_code=0,candidate_exit_code=0,
            compare_only=False,repository="timerloggedout-spec/termux-monorepo",
            run_id="12345",run_attempt="1")
        values.update(overrides)
        return build_record(**values)

    def test_success_record_matches_canonical_schema(self):
        record=self.record(); validate_record(record,SCHEMA)
        self.assertEqual(record["schema_version"],"1.0")
        self.assertEqual(record["status"],"passed")
        self.assertEqual(record["treatment"]["arm"],"candidate-vs-baseline")

    def test_failure_is_not_a_pass(self):
        record=self.record(candidate_exit_code=1); validate_record(record,SCHEMA)
        self.assertEqual(record["status"],"failed")

    def test_missing_exit_code_is_failed_not_passed(self):
        record=self.record(candidate_exit_code=None); validate_record(record,SCHEMA)
        self.assertEqual(record["status"],"failed")

    def test_compare_only_is_observed_not_passed(self):
        record=self.record(compare_only=True,baseline_exit_code=None,candidate_exit_code=None)
        validate_record(record,SCHEMA)
        self.assertEqual(record["status"],"observed")

    def test_unresolved_sha_is_rejected(self):
        with self.assertRaises(ValueError): self.record(candidate_sha="unresolved-ref")

    def test_unknown_fields_are_rejected_by_schema(self):
        record=self.record(); record["invented_success"]=True
        with self.assertRaises(Exception): validate_record(record,SCHEMA)

    def test_pre_resolution_failure_preserves_context_without_fake_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"failure.json"
            write_failure_envelope(path,experiment_id="test-002",stage="resolve-refs",
                reason="baseline ref missing",candidate_ref="feature",baseline_ref="missing",run_id="12345")
            payload=json.loads(path.read_text())
            self.assertEqual(payload["status"],"blocked")
            self.assertFalse(payload["canonical_record_emitted"])
            self.assertNotIn("baseline_sha",payload)

if __name__=="__main__": unittest.main()
