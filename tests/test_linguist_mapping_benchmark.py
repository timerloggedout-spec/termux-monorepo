import json
from pathlib import Path

import pytest

from scripts.linguist.mapping_benchmark import (
    build_dataset, mappings_from_panel_feed, validate_mappings,
)


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



def test_panel_feed_adapter_preserves_the_canonical_snapshot():
    feed_path = ROOT / "apps/tribute-dashboard/data/linguist-panel-feed.json"
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    mappings = mappings_from_panel_feed(feed)
    assert len(mappings) == feed["counts"]["entries_included"] - 1 == 522
    assert sum(item.get("feed_duplicate_count", 1) for item in mappings) == 523
    assert len({item["mapping_id"] for item in mappings}) == len(mappings)
    assert all(item["provenance"]["path"] for item in mappings)
    assert all(item["feed_generated_at"] == feed["generated_at"] for item in mappings)
    assert any(item["round_trip_status"] == "failed" for item in mappings)
    assert all(item["grade"] == "unverified" for item in mappings)
    assert any(item["grade"] == "unverified" for item in mappings)
    assert any(item["evidence_status"] == "candidate" for item in mappings)
    assert any(item.get("feed_duplicate_count") == 2 for item in mappings)
    group_labels = [item for item in mappings if item.get("feed_entry_id") == "nomenclature-labels:g"]
    assert len(group_labels) == 2
    assert len({item["mapping_id"] for item in group_labels}) == 2
    assert len({item["feed_label_id"] for item in group_labels}) == 2
    assert all(item["feed_family"] != "archwiz-pointer-index" for item in mappings)


def test_panel_feed_adapter_rejects_unknown_schema_and_skips_count_only():
    with pytest.raises(ValueError, match="unsupported Linguist panel feed schema"):
        mappings_from_panel_feed({"schema": "unknown"})

    feed = {
        "schema": "linguist-panel-feed/v1",
        "generated_at": "2026-11-05T04:02:41Z",
        "families": [{"id": "private-index", "entries_included": False}],
        "entries": [{
            "id": "private-index:opaque", "family": "private-index",
            "source": "opaque", "variants": ["pointer"], "direction": "decode-only",
            "round_trip_verified": None,
        }],
    }
    assert mappings_from_panel_feed(feed) == []



def test_panel_feed_adapter_disambiguates_reused_entry_ids():
    feed = {
        "schema": "linguist-panel-feed/v1",
        "families": [{"id": "sample", "entries_included": True}],
        "entries": [
            {
                "id": "sample:shared", "family": "sample", "source": "alpha",
                "variants": ["A"], "direction": "bidirectional",
                "provenance": {"path": "a.md", "detail": "line 1"},
                "round_trip_verified": None,
            },
            {
                "id": "sample:shared", "family": "sample", "source": "beta",
                "variants": ["B"], "direction": "bidirectional",
                "provenance": {"path": "b.md", "detail": "line 2"},
                "round_trip_verified": None,
            },
        ],
    }
    first = mappings_from_panel_feed(feed)
    second = mappings_from_panel_feed(feed)
    assert len(first) == 2
    assert first == second
    assert len({item["mapping_id"] for item in first}) == 2
    assert all(item["feed_identity_collision"] for item in first)


def test_panel_feed_adapter_collapses_exact_duplicates_with_count():
    entry = {
        "id": "sample:one", "family": "sample", "source": "alpha",
        "variants": ["A"], "direction": "bidirectional",
        "provenance": {"path": "a.md", "detail": "line 1"},
        "round_trip_verified": True,
    }
    feed = {
        "schema": "linguist-panel-feed/v1",
        "families": [{"id": "sample", "entries_included": True}],
        "entries": [entry, dict(entry)],
    }
    mappings = mappings_from_panel_feed(feed)
    assert len(mappings) == 1
    assert mappings[0]["feed_duplicate_count"] == 2



def test_round_trip_evidence_does_not_upgrade_mapping_grade():
    feed = {
        "schema": "linguist-panel-feed/v1",
        "families": [{"id": "sample", "entries_included": True}],
        "entries": [
            {
                "id": "sample:verified", "family": "sample", "source": "alpha",
                "variants": ["A"], "direction": "bidirectional",
                "provenance": {"path": "a.md", "detail": "line 1"},
                "round_trip_verified": True,
            },
            {
                "id": "sample:failed", "family": "sample", "source": "beta",
                "variants": ["B"], "direction": "bidirectional",
                "provenance": {"path": "b.md", "detail": "line 2"},
                "round_trip_verified": False,
            },
            {
                "id": "sample:candidate", "family": "sample", "source": "gamma",
                "variants": ["C"], "direction": "bidirectional",
                "provenance": {"path": "c.md", "detail": "line 3"},
                "round_trip_verified": True, "grade": "analogue",
                "relation": "related_match", "status": "candidate",
            },
        ],
    }
    by_id = {
        item["feed_entry_id"]: item for item in mappings_from_panel_feed(feed)
    }
    assert by_id["sample:verified"]["grade"] == "unverified"
    assert by_id["sample:verified"]["round_trip_status"] == "verified"
    assert by_id["sample:verified"]["evidence_status"] == "roundtrip-verified"
    assert by_id["sample:verified"]["relation"] == "maps_to"
    assert by_id["sample:failed"]["grade"] == "unverified"
    assert by_id["sample:failed"]["round_trip_status"] == "failed"
    assert by_id["sample:failed"]["evidence_status"] == "roundtrip-failed"
    assert by_id["sample:candidate"]["grade"] == "analogue"
    assert by_id["sample:candidate"]["round_trip_status"] == "verified"
    assert by_id["sample:candidate"]["evidence_status"] == "candidate"
    assert by_id["sample:candidate"]["relation"] == "related_match"
