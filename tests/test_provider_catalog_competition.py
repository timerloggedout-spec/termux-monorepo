import hashlib
import json

import pytest

from scripts.provider_catalog_competition import populate, populate_population


def test_populate_writes_both_catalogues_from_one_v5_snapshot(tmp_path):
    source = tmp_path / "incumbent-source.json"
    output = tmp_path / "catalogues"
    source_bytes = (
        b'{"schema":"provider-model-catalog/v5","observed_at":"2026-11-21T00:00:00Z",'
        b'"providers":["fixture"],"provider_observations":{"fixture":{"status":"observed"}},"models":[{"provider":"fixture","id":"model-a",'
        b'"pricing":{"prompt":"0.0001"}}]}'
    )
    source.write_bytes(source_bytes)

    manifest = populate(source, output)

    incumbent_bytes = (output / "incumbent-v5.json").read_bytes()
    inspired = json.loads((output / "vultr-inspired-v1.json").read_text(encoding="utf-8"))
    stored_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))

    assert incumbent_bytes == source_bytes
    assert inspired["catalogue"] == "VultrInspired"
    assert inspired["models"][0]["id"] == "model-a"
    assert inspired["provider_observations"] == {"fixture": {"status": "observed"}}
    assert manifest == stored_manifest
    assert manifest["source_sha256"] == hashlib.sha256(source_bytes).hexdigest()
    assert [variant["catalogue"] for variant in manifest["variants"]] == [
        "Incumbent", "VultrInspired"
    ]
    assert manifest["execution"]["network_requests"] == 0


def test_populate_rejects_non_v5_input(tmp_path):
    source = tmp_path / "wrong.json"
    source.write_text('{"schema":"other"}', encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported_incumbent_schema"):
        populate(source, tmp_path / "output")


def test_populate_full_pool_variants_from_population_v1(tmp_path):
    source = tmp_path / "population.json"
    output = tmp_path / "full-pool"
    source.write_text(json.dumps({
        "schema": "provider-model-population/v1",
        "population_version": "1.0.0",
        "provider_candidates": [{"provider_id": "g4f:Alpha"}],
        "model_candidates": [{"candidate_id": "c1", "provider_id": "Alpha", "model_id": "m1",
            "sources": ["g4f-endpoint-universe"], "evidence_classes": ["ENUMERATED_CANDIDATE"],
            "source_details": [{"source": "g4f-endpoint-universe", "evidence_class": "ENUMERATED_CANDIDATE"}],
            "runtime_eligible": False, "inference_admitted": False}],
        "source_benchmarks": {"g4f_endpoint_universe": {"pairs_total": 1}},
        "pool_counts": {"distinct_model_candidates": 1, "inference_admitted_candidates": 0}
    }), encoding="utf-8")
    manifest = populate_population(source, output)
    incumbent = (output / "incumbent-full-pool-v1.json").read_bytes()
    inspired = json.loads((output / "vultr-inspired-full-pool-v2.json").read_text(encoding="utf-8"))
    assert incumbent == source.read_bytes()
    assert inspired["catalogue"] == "VultrInspired"
    assert inspired["models"][0]["id"] == "m1"
    assert inspired["models"][0]["lifecycle"]["inference_admitted"] is False
    assert manifest["variants"][0]["model_count"] == 1
    assert manifest["variants"][1]["model_count"] == 1
    assert manifest["execution"]["network_requests"] == 0
