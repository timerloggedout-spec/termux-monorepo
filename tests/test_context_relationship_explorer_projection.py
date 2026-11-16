from copy import deepcopy

from archwiz.context_relationships.explorer_projection import project_coverage


def sample():
    manifest = {
        "node_count": 3,
        "edge_count": 4,
        "verified_edge_count": 3,
        "candidate_edge_count": 1,
        "latest_observed_at": "2026-10-15T19:16:02.945529Z",
        "history_window": {
            "start_page": 13,
            "next_start_page": None,
            "pull_request_count": 0,
        },
        "github_report": {
            "checkpoint_eligible": False,
            "counts": {"pull_request_window_stubs": 2},
        },
    }
    summary = {
        "coverage": "COMPLETE",
        "node_count": 3,
        "edge_count": 4,
        "verified_edge_count": 3,
        "candidate_edge_count": 1,
    }
    return manifest, summary


def test_projection_preserves_declared_coverage_and_flags_contradictions():
    manifest, summary = sample()
    result = project_coverage(
        manifest,
        summary,
        source_ref="master",
        source_sha="a" * 40,
        manifest_blob_sha="b" * 40,
    )

    assert result["coverage"]["status"] == "COMPLETE"
    assert result["coverage"]["next_start_page"] is None
    assert result["coverage"]["checkpoint_eligibility"] == "INELIGIBLE"
    assert result["reconciliation"]["status"] == "RECONCILIATION_REQUIRED"
    codes = {finding["code"] for finding in result["reconciliation"]["findings"]}
    assert "COMPLETE_BUT_CHECKPOINT_INELIGIBLE" in codes
    assert "PR_WINDOW_STUBS_WITH_ZERO_DECLARED_PR_COUNT" in codes
    assert result["provenance"]["provenance_complete"] is True


def test_projection_flags_count_mismatch_without_overwriting_source_counts():
    manifest, summary = sample()
    summary["edge_count"] = 99

    result = project_coverage(
        manifest,
        summary,
        source_ref="master",
        source_sha="a" * 40,
        manifest_blob_sha="b" * 40,
    )

    assert result["counts"]["edges"] == 4
    assert result["reconciliation"]["status"] == "RECONCILIATION_REQUIRED"
    assert any(
        finding["code"] == "COUNT_MISMATCH"
        and finding["field"] == "edges"
        for finding in result["reconciliation"]["findings"]
    )


def test_unknown_counts_remain_unavailable_not_zero():
    manifest, summary = sample()
    del manifest["node_count"]
    del summary["node_count"]

    result = project_coverage(
        manifest,
        summary,
        source_ref="master",
        source_sha="a" * 40,
        manifest_blob_sha="b" * 40,
    )

    assert result["counts"]["nodes"] is None
    assert any(
        finding["code"] == "COUNT_UNAVAILABLE"
        for finding in result["reconciliation"]["findings"]
    )


def test_invalid_provenance_fails_closed():
    manifest, summary = sample()
    result = project_coverage(
        manifest,
        summary,
        source_ref="",
        source_sha="not-a-sha",
        manifest_blob_sha="not-a-blob",
    )

    assert result["provenance"]["provenance_complete"] is False
    assert result["provenance"]["source_sha"] is None
    assert result["reconciliation"]["status"] == "RECONCILIATION_REQUIRED"
    assert result["reconciliation"]["error_count"] == 3


def test_projection_does_not_mutate_source_objects():
    manifest, summary = sample()
    original_manifest = deepcopy(manifest)
    original_summary = deepcopy(summary)

    project_coverage(
        manifest,
        summary,
        source_ref="master",
        source_sha="a" * 40,
        manifest_blob_sha="b" * 40,
    )

    assert manifest == original_manifest
    assert summary == original_summary
