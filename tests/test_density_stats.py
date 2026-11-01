import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "density_stats", ROOT / "scripts/telemetry_ingest/density_stats.py")
ds = importlib.util.module_from_spec(spec); spec.loader.exec_module(ds)

def test_signal_units_deterministic_and_weighted():
    dense = ds.signal_units("PR #123 merged 8c36004e verified: 21/21 PASS, see docs/ops/X.md https://example.com/r")
    empty = ds.signal_units("This is a long explanatory paragraph about things in general terms and prose.")
    assert dense["density"] > empty["density"]
    assert dense["identifiers"] >= 3 and dense["verdicts"] >= 2
    assert ds.signal_units("PR #123 merged") == ds.signal_units("PR #123 merged")

def test_restatement_penalized():
    once = ds.signal_units("PR #1 merged 8c36004e. PR #2 landed 9b192841.")
    twice = ds.signal_units("PR #1 merged 8c36004e. PR #2 landed 9b192841. PR #1 merged 8c36004e. PR #2 landed 9b192841.")
    assert twice["restatement_penalty"] > 0
    assert twice["density"] < once["density"]

def test_spearman_perfect_and_reverse():
    assert ds.spearman([1, 2, 3, 4, 5], [10, 20, 30, 40, 50])["rho"] == 1.0
    assert ds.spearman([1, 2, 3, 4, 5], [50, 40, 30, 20, 10])["rho"] == -1.0

def test_association_gate_small_minority_not_established():
    rows = [{"density": 0.1 * i, "outcome_value": 1.0} for i in range(1, 40)]
    rows += [{"density": 0.05, "outcome_value": 0.0}, {"density": 0.06, "outcome_value": 0.0}]
    a = ds.association(rows, "merged")
    assert a["verdict"] == "NOT_ESTABLISHED"
    assert any("minority" in r for r in a["reasons"])

def test_build_shapes_and_pending_excluded():
    prs = [{"number": 1, "title": "feat: x PR #1", "body": "merged 8c36004e",
            "head": {"ref": "lane-a/work"}, "merged_at": "2026-01-01T00:00:00Z", "state": "closed"},
           {"number": 2, "title": "wip", "body": "", "head": {"ref": "lane-a/wip"},
            "merged_at": None, "state": "open"}]
    feed = {"rfps": [{"number": 9, "title": "[delphi:rfp] x.y", "lane": "data",
                      "questions": [{"response": "NEON_API_KEY present, limit 42"}],
                      "outcome": {"effective_score": 7.5}}]}
    stats, payloads = ds.build(prs, feed, "t")
    kinds = {(a["artifact_id"], a["outcome_state"]) for a in stats["artifacts"]}
    assert ("pr-1", "merged") in kinds and ("pr-2", "pending") in kinds
    assert stats["artifacts"][2]["outcome_value"] == 7.5
    assert all(p["sink"] == "hindsight" for p in payloads)
    assert stats["evidence_hash"]
