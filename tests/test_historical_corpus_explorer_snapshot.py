import json

from scripts.ci.build_historical_corpus_explorer_snapshot import build_projection


def test_builder_binds_provenance_and_keeps_coverage_findings():
    manifest = {
        "node_count": 10,
        "edge_count": 12,
        "verified_edge_count": 9,
        "candidate_edge_count": 3,
        "latest_observed_at": "2026-10-15T19:16:02.945529Z",
        "history_window": {"start_page": 13, "next_start_page": None, "pull_request_count": 0},
        "github_report": {"checkpoint_eligible": False, "counts": {"pull_request_window_stubs": 18}},
    }
    summary = {
        "coverage": "COMPLETE",
        "node_count": 10,
        "edge_count": 12,
        "verified_edge_count": 9,
        "candidate_edge_count": 3,
    }

    projection = build_projection(
        manifest,
        summary,
        source_ref="master",
        source_sha="a" * 40,
        manifest_blob_sha="b" * 40,
    )

    assert projection["snapshot_id"] == "hce-" + "a" * 12 + "-" + "b" * 12
    assert projection["provenance"]["source_sha"] == "a" * 40
    assert projection["provenance"]["manifest_blob_sha"] == "b" * 40
    assert projection["coverage"]["status"] == "COMPLETE"
    assert projection["reconciliation"]["status"] == "RECONCILIATION_REQUIRED"
    assert {item["code"] for item in projection["reconciliation"]["findings"]} >= {
        "COMPLETE_BUT_CHECKPOINT_INELIGIBLE",
        "PR_WINDOW_STUBS_WITH_ZERO_DECLARED_PR_COUNT",
    }


def test_builder_emits_deterministic_projection():
    manifest = {
        "node_count": 1, "edge_count": 0, "verified_edge_count": 0,
        "candidate_edge_count": 0, "latest_observed_at": "2026-10-01T00:00:00Z",
        "history_window": {"start_page": 1, "next_start_page": 2, "pull_request_count": 0},
    }
    summary = {
        "coverage": "PARTIAL_CONTINUATION_REQUIRED", "node_count": 1, "edge_count": 0,
        "verified_edge_count": 0, "candidate_edge_count": 0,
    }
    args = {
        "source_ref": "feature",
        "source_sha": "c" * 40,
        "manifest_blob_sha": "d" * 40,
    }
    assert build_projection(manifest, summary, **args) == build_projection(manifest, summary, **args)
