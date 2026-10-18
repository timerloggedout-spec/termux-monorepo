import unittest

from scripts.ci.procurement_edge_contract_validator import (
    validate_edge_evidence,
    validate_manager_tournament,
    validate_procurement_record,
)


def procurement_record():
    return {
        "resource_id": "example-runtime",
        "project": "Example Runtime",
        "canonical_source": "https://example.org/",
        "license": "Apache-2.0",
        "maintenance": "Release history reviewed 2026-10-17",
        "portability": {
            "arm64_linux": "VERIFY",
            "x86_64_linux": "VERIFY",
            "android": "VERIFY",
            "termux": "VERIFY",
            "offline_airgapped": "VERIFY",
        },
        "offline_capability": "VERIFY",
        "interoperability": "JSONL export",
        "reproducibility": "Version pin required",
        "provenance": "Official project documentation",
        "dependency_risk": "Medium",
        "lock_in_risk": "Low",
        "security_surface": "Local runtime",
        "resource_cost": "FOSS; compute cost not measured",
        "operational_fit": "Prototype only",
        "horizon": "H1",
        "confidence": "medium",
        "decision_status": "PROTOTYPE",
        "version_or_commit": "VERIFY",
        "observed_at": "2026-10-17T12:00:00Z",
        "unresolved_questions": ["Does the Android build work offline?"],
    }


def edge_record():
    return {
        "schema_version": "edge.inference.v1",
        "experiment_id": "test-only-fixture",
        "device_abi": "arm64-v8a",
        "device_model": None,
        "os_version": None,
        "model_hash": "a" * 64,
        "model_family": "fixture-only",
        "quantization": "Q4_K_M",
        "runtime": "fixture-runtime",
        "runtime_version": "1.0.0",
        "backend": "cpu",
        "tokens_per_second": None,
        "latency_p50_ms": None,
        "latency_p95_ms": None,
        "peak_memory_mb": None,
        "thermal_state": None,
        "energy_proxy": None,
        "offline": True,
        "fallback_path": None,
        "observed_at": "2026-10-17T12:00:00Z",
        "provenance": {
            "repository_sha": "b" * 40,
            "environment_fingerprint": "c" * 64,
            "runtime_source": "https://example.org/runtime",
            "model_source": None,
        },
    }


def manager_record():
    return {
        "schema_version": "manager.tournament.v1",
        "tournament_id": "fixture-tournament",
        "cohort_id": "fixture-cohort",
        "policy_version": "1",
        "task_contract_hash": "a" * 64,
        "environment_fingerprint": "b" * 64,
        "managers": [
            {"manager_id": "serial", "policy_hash": "c" * 64, "routing_policy": "serial"},
            {"manager_id": "parallel", "policy_hash": "d" * 64, "routing_policy": "parallel"},
        ],
        "evaluation_contract": {
            "acceptance": "same task set and acceptance tests",
            "evidence_schema": "agent.throughput.v1",
            "repetitions": 3,
        },
        "provenance": {
            "created_at": "2026-10-17T12:00:00Z",
            "repository_sha": "e" * 40,
            "benchmark_source": "https://example.org/benchmark",
        },
    }


class ProcurementEdgeContractTests(unittest.TestCase):
    def test_existing_procurement_shape_is_valid(self):
        self.assertEqual(validate_procurement_record(procurement_record()), [])

    def test_rejects_adopt_without_tested_portability_and_version(self):
        record = procurement_record()
        record["decision_status"] = "ADOPT"
        errors = validate_procurement_record(record)
        self.assertTrue(any("ADOPT requires verified version_or_commit" in error for error in errors))
        self.assertTrue(any("ADOPT requires explicit tested/verified status for portability.termux" in error for error in errors))

    def test_accepts_adopt_only_with_explicit_tested_target_statuses(self):
        record = procurement_record()
        record["decision_status"] = "ADOPT"
        record["license"] = "Apache-2.0"
        record["maintenance"] = "Maintained; release reviewed 2026-10-17"
        record["version_or_commit"] = "v1.2.3"
        record["offline_capability"] = "Offline tested: pass"
        record["portability"] = {key: "TESTED: PASS" for key in record["portability"]}
        self.assertEqual(validate_procurement_record(record), [])

    def test_rejects_invalid_source_horizon_and_timestamp(self):
        record = procurement_record()
        record["canonical_source"] = "file:///etc/passwd"
        record["horizon"] = "H9"
        record["observed_at"] = "2026-10-17T12:00:00-07:00"
        errors = validate_procurement_record(record)
        self.assertTrue(any("canonical_source" in error for error in errors))
        self.assertTrue(any("horizon" in error for error in errors))
        self.assertTrue(any("observed_at" in error for error in errors))

    def test_edge_evidence_allows_missing_measurements_as_null(self):
        self.assertEqual(validate_edge_evidence(edge_record()), [])

    def test_edge_evidence_rejects_bad_hash_negative_metric_and_unknown_field(self):
        record = edge_record()
        record["model_hash"] = "not-a-hash"
        record["tokens_per_second"] = -1
        record["device_serial"] = "must-not-be-stored"
        errors = validate_edge_evidence(record)
        self.assertTrue(any("model_hash" in error for error in errors))
        self.assertTrue(any("tokens_per_second" in error for error in errors))
        self.assertTrue(any("unknown fields" in error for error in errors))

    def test_edge_evidence_requires_runtime_and_environment_provenance(self):
        record = edge_record()
        record["provenance"].pop("repository_sha")
        record["runtime"] = ""
        errors = validate_edge_evidence(record)
        self.assertTrue(any("provenance.repository_sha" in error for error in errors))
        self.assertTrue(any("runtime" in error for error in errors))

    def test_manager_tournament_contract_is_reproducible(self):
        self.assertEqual(validate_manager_tournament(manager_record()), [])

    def test_manager_tournament_rejects_duplicate_manager_ids_and_zero_repetitions(self):
        record = manager_record()
        record["managers"].append(record["managers"][0].copy())
        record["evaluation_contract"]["repetitions"] = 0
        errors = validate_manager_tournament(record)
        self.assertTrue(any("duplicate manager ID" in error for error in errors))
        self.assertTrue(any("repetitions" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
