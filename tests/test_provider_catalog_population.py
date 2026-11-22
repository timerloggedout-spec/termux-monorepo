import pytest
from scripts.provider_catalog_population import compile_population

def sources():
    return (
        {"schema":"desk-feed/v1.3","dispatch":{"provider_catalog":{
            "inference_only":{"class":"inference-only","model_records":2,
                "distinct_providers":["native-a","g4f/Alpha"],"registry_ids":["a","b"],
                "provider_classes":{"proven":{"providers":["native-a"]}}},
            "endpoint_census":{"verified_floor":7341,"counted_at":"2026-11-01","sources":{"catalog":{"models":20}}}
        }}},
        {"services":[{"id":"native-a.model","provider":"native-a","lane":"model"},
                     {"id":"github.ci","provider":"github","lane":"ci"}]},
        {"schema_version":"g4f-working-catalog-v1","summary":{"models_catalogued":2},
         "providers":[{"id":"Alpha","runtime_eligible":False,"evidence_class":"REFERENCE_ONLY",
             "model_count":2,"models":["m1","m2"],"working_models":[{"model":"m1","type":"text"}]}]},
        {"schema":"g4f-endpoint-universe/v1","g4f_version":"8.8.16","providers_total":1,
         "pairs_total":2,"counts_by_source":{"both":1,"upstream-g4f":1},
         "pairs":[{"provider":"Alpha","model":"m1","source":"both"},
                  {"provider":"Alpha","model":"m3","source":"upstream-g4f"}]},
    )

def test_full_pool_layers_and_evidence_classes():
    p=compile_population(*sources()); b=p["source_benchmarks"]
    assert b["quota_service_registry"]["service_records"] == 2
    assert b["dispatch_model_bench"]["model_records"] == 2
    assert b["g4f_working_catalog"]["providers"] == 1
    assert b["g4f_working_catalog"]["distinct_model_pairs"] == 2
    assert b["g4f_working_catalog"]["reported_working_pairs"] == 1
    assert b["g4f_endpoint_universe"]["pairs_total"] == 2
    assert b["historical_actions_verified_endpoint_floor"]["count"] == 7341
    assert p["pool_counts"]["distinct_model_candidates"] == 3
    assert p["pool_counts"]["inference_admitted_candidates"] == 0

def test_exact_pair_join_preserves_sources_and_closed_runtime_gate():
    p=compile_population(*sources())
    row=next(x for x in p["model_candidates"] if x["model_id"]=="m1")
    assert set(row["sources"]) == {"g4f-endpoint-universe","g4f-working-catalog","g4f-working-probe-summary"}
    assert "ENUMERATED_CANDIDATE" in row["evidence_classes"]
    assert row["runtime_eligible"] is False and row["inference_admitted"] is False

def test_rejects_universe_count_mismatch():
    desk, quota, catalog, universe=sources(); universe["pairs_total"]=99
    with pytest.raises(ValueError,match="g4f_universe_pair_count_mismatch"):
        compile_population(desk,quota,catalog,universe)

def test_rejects_unknown_catalog_schema():
    desk, quota, catalog, universe=sources(); catalog["schema_version"]="other"
    with pytest.raises(ValueError,match="unsupported_g4f_catalog_schema"):
        compile_population(desk,quota,catalog,universe)
