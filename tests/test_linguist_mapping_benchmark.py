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
    assert first["stats"]["mappings"] == 4
    assert first["stats"]["queries"] == 4


def test_qrels_preserve_exact_and_approximate_grades():
    dataset = build_dataset(load_mappings())
    by_id = dataset["corpus"]
    assert by_id["fleet-lean-matrix-cell"]["grade"] == "exact"
    assert by_id["fleet-lean-matrix-composition"]["grade"] == "approximate"
    assert by_id["fleet-lean-matrix-composition"]["kernel"]


def test_same_surface_across_domains_is_reported_as_conflict_group():
    dataset = build_dataset(load_mappings())
    assert len(dataset["conflicts"]) == 1
    conflict = dataset["conflicts"][0]
    assert conflict["source_form"] == "∘"
    assert set(conflict["mapping_ids"]) == {
        "fleet-lean-matrix-composition",
        "fixture-only-lean-function-composition",
    }


def test_domain_scoping_keeps_overloaded_symbol_qrels_separate():
    dataset = build_dataset(load_mappings())
    matrix_query = next(
        query_id for query_id, query in dataset["queries"].items()
        if query["domain"] == "matrices" and query["semantic_id"] == "matrix.composition"
    )
    category_query = next(
        query_id for query_id, query in dataset["queries"].items()
        if query["domain"] == "functions"
    )
    assert dataset["qrels"][matrix_query] == {"fleet-lean-matrix-composition": 1}
    assert dataset["qrels"][category_query] == {"fixture-only-lean-function-composition": 1}
    assert set(dataset["candidates"][matrix_query]) >= {
        "fleet-lean-matrix-composition",
        "fixture-only-lean-function-composition",
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
