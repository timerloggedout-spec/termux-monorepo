import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("iie_benchmark", ROOT / "scripts/ops/iie_benchmark.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def receipt(**overrides):
    value = {
        "repository": "example/repo",
        "ref": "main",
        "source_sha": "a" * 40,
        "nodes_sha256": "b" * 64,
        "edges_sha256": "c" * 64,
        "node_count": 10,
        "edge_count": 20,
        "verified_edge_count": 15,
        "candidate_edge_count": 5,
        "coverage": "COMPLETE",
        "github_requests": 100,
        "performance": {
            "wall_seconds": 20.0,
            "process_cpu_seconds": 10.0,
            "peak_rss_bytes": 1000,
        },
    }
    value.update(overrides)
    return value


def test_comparison_requires_deterministic_parity():
    baseline = receipt()
    treatment = receipt(github_requests=50, performance={
        "wall_seconds": 10.0, "process_cpu_seconds": 5.0, "peak_rss_bytes": 900,
    })
    result = MODULE.compare(baseline, treatment)
    assert result["status"] == "PARITY_PASSED"
    assert result["metrics"]["github_requests"]["speedup_or_reduction_ratio"] == 2.0
    assert result["metrics"]["wall_seconds"]["speedup_or_reduction_ratio"] == 2.0


def test_comparison_rejects_coverage_or_graph_drift():
    result = MODULE.compare(receipt(), receipt(edge_count=19, coverage="PARTIAL", edges_sha256="d" * 64))
    assert result["status"] == "PARITY_FAILED"
    assert set(result["parity_mismatches"]) == {"edge_count", "coverage", "edges_sha256"}


def test_ratio_handles_missing_and_zero_values():
    assert MODULE.ratio(None, 2) is None
    assert MODULE.ratio(0, 2) is None
    assert MODULE.ratio(4, 0) is None



def test_load_receipt_rejects_missing_source_identity(tmp_path):
    import json
    import pytest

    path = tmp_path / "receipt.json"
    invalid = receipt()
    invalid.pop("source_sha")
    path.write_text(json.dumps(invalid), encoding="utf-8")
    with pytest.raises(ValueError, match="source_sha"):
        MODULE.load_receipt(path)
