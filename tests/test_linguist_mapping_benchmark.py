import json
from pathlib import Path

import pytest

from scripts.linguist.mapping_benchmark import build_dataset, validate_mappings


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "experiments/linguist/mapping-benchmarks/fixtures/fleet-lean-mappings.json"


def load_mappings():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["mappings"]


def test_benchmark_generation_is_deterministic():
    mappings = load_mappings()
    first = build_dataset(mappings, seed=42)
    second = build_dataset(mappings, seed=42)
    assert first == second
    assert first["schema"] == "linguist-mapping-benchmark/v1"
    assert first["stats"]["mappings"] == 30
    assert first["stats"]["queries"] == 30
    assert first["stats"]["evidence_status"] == {
        "candidate": 14, "proof-verified": 2, "spec-level": 11, "unspecified": 3
    }


def test_qrels_preserve_grade_kernel_and_evidence_state():
    dataset = build_dataset(load_mappings())
    by_id = dataset["corpus"]
    assert by_id["fleet-lean-matrix-cell"]["grade"] == "exact"
    assert by_id["fleet-lean-matrix-composition"]["grade"] == "approximate"
    assert by_id["fleet-lean-matrix-composition"]["kernel"]
    assert by_id["fleet-lean-function-composition"]["evidence_status"] == "proof-verified"
    assert by_id["fleet-lean-matrix-identity"]["evidence_status"] == "proof-verified"
    assert by_id["nomenclature-map-bind-not-compose"]["grade"] == "analogue"
    assert by_id["nomenclature-map-bind-not-compose"]["evidence_status"] == "candidate"
    assert by_id["nomenclature-map-bind-not-compose"]["relation"] == "related_match"


def test_same_surface_across_domains_is_reported_as_conflict_group():
    dataset = build_dataset(load_mappings())
    conflicts = {
        conflict["source_form"]: set(conflict["mapping_ids"])
        for conflict in dataset["conflicts"]
    }
    assert conflicts["∘"] == {
        "fleet-lean-matrix-composition",
        "fleet-lean-function-composition",
    }
    assert conflicts["dual_valence.conversion_operator"] == {
        "nomenclature-map-dv-conversion-morphism",
        "nomenclature-map-dv-conversion-homomorphism",
    }


def test_domain_scoping_keeps_overloaded_symbol_qrels_separate():
    dataset = build_dataset(load_mappings())
    matrix_query = next(
        query_id for query_id, query in dataset["queries"].items()
        if query["domain"] == "matrices" and query["semantic_id"] == "matrix.composition"
    )
    function_query = next(
        query_id for query_id, query in dataset["queries"].items()
        if query["domain"] == "functions"
    )
    assert dataset["qrels"][matrix_query] == {"fleet-lean-matrix-composition": 1}
    assert dataset["qrels"][function_query] == {"fleet-lean-function-composition": 1}
    assert set(dataset["candidates"][matrix_query]) >= {
        "fleet-lean-matrix-composition",
        "fleet-lean-function-composition",
    }


def test_invalid_grade_and_missing_provenance_fail_validation():
    mappings = load_mappings()
    mappings[0]["grade"] = "certain"
    with pytest.raises(ValueError, match="unsupported grade"):
        validate_mappings(mappings)

    mappings = load_mappings()
    mappings[0]["provenance"] = {}
    with pytest.raises(ValueError, match="provenance is required"):
        validate_mappings(mappings)


def test_duplicate_mapping_ids_fail_validation():
    mappings = load_mappings()
    mappings[1]["mapping_id"] = mappings[0]["mapping_id"]
    with pytest.raises(ValueError, match="duplicate mapping_id"):
        validate_mappings(mappings)


def test_retrieval_metrics_reward_correct_top_rank():
    from scripts.linguist.mapping_benchmark import evaluate_rankings

    dataset = build_dataset(load_mappings())
    rankings = {
        query_id: [next(iter(relevant)), *[
            mapping_id for mapping_id in dataset["candidates"][query_id]
            if mapping_id not in relevant
        ]]
        for query_id, relevant in dataset["qrels"].items()
    }
    scored = evaluate_rankings(dataset, rankings, ks=(1, 3))
    assert scored["query_count"] == len(dataset["queries"])
    assert scored["aggregate"]["mrr"] == 1.0
    assert scored["aggregate"]["precision@1"] == 1.0
    assert scored["aggregate"]["recall@1"] == 1.0
    assert scored["aggregate"]["ndcg@1"] == 1.0


def test_retrieval_metrics_report_empty_rankings_as_zero():
    from scripts.linguist.mapping_benchmark import evaluate_rankings

    dataset = build_dataset(load_mappings())
    scored = evaluate_rankings(dataset, {})
    assert scored["aggregate"]["mrr"] == 0.0
    assert scored["aggregate"]["recall@1"] == 0.0


def test_retrieval_metrics_reject_unknown_mapping_ids():
    from scripts.linguist.mapping_benchmark import evaluate_rankings

    dataset = build_dataset(load_mappings())
    query_id = next(iter(dataset["queries"]))
    with pytest.raises(ValueError, match="unknown mapping ids"):
        evaluate_rankings(dataset, {query_id: ["missing-mapping"]})
