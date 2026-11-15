import json
from pathlib import Path

from scripts.ops.provider_population_census import build_census


def write_json(root: Path, relative: str, value: dict) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def fixture_repo(tmp_path: Path) -> Path:
    write_json(tmp_path, "ops/challenge/desk-feed.json", {
        "dispatch": {"provider_catalog": {
            "census": {"registry": {"services_total": 164, "distinct_providers_all_lanes": 110,
                                    "model_records": 91, "model_distinct_providers": 89}},
            "inference_wiring": {"wired_invoke": {"count": 92, "of": 93},
                                 "not_wired": {"count": 0}},
            "endpoint_census": {"verified_floor": 7341, "counted_at": "2026-11-01 (Actions census)"},
            "inference_availability": {"summary": {"records": 95, "by_class": {"wired-unproven": 23, "triggerable": 2, "inference-only": 65, "proven": 5}, "availability_covered": 16, "availability_secret_only": 1, "availability_not_covered": 74, "batch_endpoint_wired": 14}},
        }}
    })
    write_json(tmp_path, "ops/quota/registry.json", {"services": []})
    write_json(tmp_path, "data/g4f-working/providers.json", {
        "providers": [{"model_count": 2}, {"model_count": 3}]
    })
    write_json(tmp_path, "data/g4f-working/universe.json", {
        "fork_pairs_raw": 5, "fork_pairs_distinct": 4, "providers_total": 3, "pairs_total": 8
    })
    write_json(tmp_path, "data/g4f-working/working-endpoints.json", {
        "attempted": 8, "inference_ok": 2, "probed_at": "2026-11-14T12:00:00Z",
        "endpoints": [{"provider": "a", "model": "x"}, {"provider": "b", "model": "y"}]
    })
    write_json(tmp_path, "ops/dispatch/build-arms.json", {"arms": [{"arm_id": "a"}, {"arm_id": "b"}]})
    write_json(tmp_path, "ops/que/feeds/arm-census.json", {
        "generated_at": "2026-11-14T12:00:00Z",
        "arms": [{"arm_id": "a", "verdict": "passed"}, {"arm_id": "b", "verdict": "failed"}]
    })
    return tmp_path


def test_population_census_keeps_all_denominators_separate(tmp_path):
    root = fixture_repo(tmp_path)
    report = build_census(root, adapter_counts={
        "catalog_adapters": 95, "native_invoke_adapters": 29,
        "workflow_menu_choices": 31, "menu_supported_by_native_adapter": 29,
        "menu_without_native_adapter": ["felo", "omni"],
        "native_adapters_not_in_menu": [],
    })
    canonical = report["canonical_population"]
    assert canonical["all_lane_distinct_providers"] == 110
    assert canonical["model_lane_distinct_providers"] == 89
    assert canonical["invoke_wiring_records"] == 92
    assert canonical["invoke_wiring_record_denominator"] == 93
    assert canonical["invoke_wiring_excluded_by_kind_records"] == 1
    assert canonical["endpoint_verified_floor"] == 7341
    assert canonical["inference_availability_records"] == 95
    assert canonical["availability_covered_records"] == 16
    assert canonical["availability_not_covered_records"] == 74
    assert report["adapter_population"]["workflow_menu_choices"] == 31
    assert report["adapter_population"]["menu_supported_by_native_adapter"] == 29
    assert report["g4f_population"]["catalog_fork_pairs_distinct"] == 4
    assert report["g4f_population"]["universe_pairs_total"] == 8
    assert report["g4f_population"]["historical_probe_inference_ok"] == 2
    assert report["build_dispatch"]["configured_build_arms"] == 2
    assert report["build_dispatch"]["arm_census_verdicts"] == {"passed": 1, "failed": 1}
    assert report["status"] == "complete_inventory"


def test_policy_and_receipt_counts_do_not_imply_dispatch_eligibility(tmp_path):
    root = fixture_repo(tmp_path)
    policy = write_json(tmp_path, "policy.json", {
        "schema": "research-provider-admission/v1",
        "entries": [{"provider": "groq", "model": "m1"}, {"provider": "groq", "model": "m2"}],
    })
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    write_json(receipts, "groq/receipt.json", {
        "schema": "provider-inference-validation/v1", "provider": "groq", "model": "m1",
        "observed_at": "2026-11-15T12:00:00Z", "validation_status": "inference_validated",
        "inference_status": "passed", "policy_admitted": True, "no_cost_verified": True,
        "dispatch_eligible": False,
    })
    report = build_census(root, policy_path=policy, receipts_dir=receipts,
                          adapter_counts={"catalog_adapters": 95})
    assert report["policy"]["entry_count"] == 2
    assert report["policy"]["provider_count"] == 1
    assert report["policy"]["exact_pair_count"] == 2
    assert report["validation_receipts"]["inference_validated"] == 1
    assert report["validation_receipts"]["dispatch_eligible"] == 0


def test_census_reports_missing_optional_live_sources_as_unavailable(tmp_path):
    root = fixture_repo(tmp_path)
    report = build_census(root, adapter_counts={})
    assert report["policy"]["supplied"] is False
    assert report["validation_receipts"]["supplied"] is False
    assert report["availability_observation"]["supplied"] is False
    assert report["cadence"]["supplied"] is False



def test_census_ingests_current_g4f_receipt_without_promoting_dispatch(tmp_path):
    root = fixture_repo(tmp_path)
    receipt = write_json(tmp_path, "g4f-inference-smoke.json", {
        "schema": "g4f-inference-smoke/v1",
        "observed_at": "2026-11-15T12:00:00Z",
        "source": "universe",
        "offset": 200,
        "limit": 200,
        "source_population_total": 9588,
        "attempted": 2,
        "inference_ok": 1,
        "providers_ok": ["ProviderA"],
        "results": [
            {"provider": "ProviderA", "model": "m1", "inference_ok": True, "error": None},
            {"provider": "ProviderB", "model": "m2", "inference_ok": False, "error": "TimeoutError"},
        ],
        "dispatch_eligible": False,
        "quota_class": "unclassified",
    })
    report = build_census(root, g4f_receipt_path=receipt, adapter_counts={})
    live = report["g4f_live_validation"]
    assert live["supplied"] is True
    assert live["source"] == "universe" and live["offset"] == 200
    assert live["attempted"] == 2 and live["inference_ok"] == 1
    assert live["providers_ok_count"] == 1
    assert live["dispatch_eligible"] == 0
    assert live["quota_class"] == "unclassified"
    assert report["g4f_receipt_source"]["sha256"]
