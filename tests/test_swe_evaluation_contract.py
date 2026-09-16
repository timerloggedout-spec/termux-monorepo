from __future__ import annotations

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "ci" / "swe_evaluation_contract.py"
SPEC = importlib.util.spec_from_file_location("swe_evaluation_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)


def manifest(**overrides):
    base = {
        "schema_version": 2,
        "run_id": "mini-swe-smoke-20260818",
        "reference": "mini-swe-agent",
        "reference_revision": "a83fcae82d2a08f0ee0c688f9d137b3566c097f8",
        "benchmark": "lite",
        "split": "dev",
        "slice": "0:1",
        "model_id": "example/model-v1",
        "started_at": "2026-08-18T12:00:00Z",
        "finished_at": "2026-08-18T12:01:00Z",
        "runner_exit_code": 0,
        "agent_completed_instances": 1,
        "benchmark_resolved_instances": None,
        "evaluation_state": "agent-run-complete",
    }
    base.update(overrides)
    base["result_digest"] = CONTRACT.digest(base)
    return base


def manifest_arguments(root: Path, predictions: Path, output: Path) -> list[str]:
    return [
        "manifest",
        "--output", str(output),
        "--run-id", "mini-swe-smoke-20260818",
        "--reference", "mini-swe-agent",
        "--reference-revision", "a83fcae82d2a08f0ee0c688f9d137b3566c097f8",
        "--benchmark", "lite",
        "--split", "dev",
        "--model-id", "example/model-v1",
        "--started-at", datetime(2026, 8, 18, 12, 0, tzinfo=UTC).isoformat(),
        "--finished-at", datetime(2026, 8, 18, 12, 1, tzinfo=UTC).isoformat(),
        "--runner-exit-code", "0",
        "--predictions", str(predictions),
    ]


class SweEvaluationContractTests(TestCase):
    def test_valid_manifest_is_accepted(self):
        CONTRACT.validate(manifest())

    def test_digest_mismatch_is_rejected(self):
        payload = manifest()
        payload["result_digest"] = "0" * 64
        with self.assertRaisesRegex(CONTRACT.ContractError, "result_digest"):
            CONTRACT.validate(payload)

    def test_unbounded_slice_is_rejected(self):
        payload = manifest(slice="0:8")
        payload["result_digest"] = CONTRACT.digest(payload)
        with self.assertRaisesRegex(CONTRACT.ContractError, "slice"):
            CONTRACT.validate(payload)

    def test_credential_shaped_value_is_rejected(self):
        payload = manifest(model_id="sk-abcdefghijklmnopqrstuv")
        payload["result_digest"] = CONTRACT.digest(payload)
        with self.assertRaisesRegex(CONTRACT.ContractError, "credential"):
            CONTRACT.validate(payload)

    def test_resolved_count_cannot_exceed_completed(self):
        payload = manifest(benchmark_resolved_instances=2)
        payload["result_digest"] = CONTRACT.digest(payload)
        with self.assertRaisesRegex(CONTRACT.ContractError, "resolved"):
            CONTRACT.validate(payload)

    def test_success_requires_exactly_one_prediction(self):
        payload = manifest(agent_completed_instances=0)
        payload["result_digest"] = CONTRACT.digest(payload)
        with self.assertRaisesRegex(CONTRACT.ContractError, "exactly one prediction"):
            CONTRACT.validate(payload)

    def test_manifest_command_counts_predictions_without_publishing_patches(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            predictions = root / "preds.json"
            predictions.write_text(json.dumps({"one": {"model_patch": "diff --git a/x"}}), encoding="utf-8")
            output = root / "result.json"
            code = CONTRACT.main(manifest_arguments(root, predictions, output))
            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["agent_completed_instances"], 1)
            self.assertNotIn("model_patch", json.dumps(payload))
            CONTRACT.validate(payload)

    def test_manifest_command_rejects_missing_predictions_for_successful_run(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing.json"
            output = root / "result.json"
            self.assertEqual(CONTRACT.main(manifest_arguments(root, missing, output)), 1)
            self.assertFalse(output.exists())

    def test_manifest_command_rejects_empty_predictions_for_successful_run(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            predictions = root / "preds.json"
            predictions.write_text("{}", encoding="utf-8")
            output = root / "result.json"
            self.assertEqual(CONTRACT.main(manifest_arguments(root, predictions, output)), 1)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    main()
