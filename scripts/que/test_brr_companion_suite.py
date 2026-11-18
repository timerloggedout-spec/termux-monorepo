"""#5552 — BRR companion regression suite (pure logic)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brr_companion_suite as s  # noqa: E402

REG = {"schema": "branch-reconciliation-registry/v1", "generated_at": "2026-11-18T00:00:00Z", "branches": [
    {"branch": "feat/a-x", "sha": "a1", "disposition": "ahead-only", "ahead_of_default": 2, "behind_default": 0},
    {"branch": "feat/b-y", "sha": "b1", "disposition": "diverged", "ahead_of_default": 1, "behind_default": 9},
    {"branch": "fix/c", "sha": "c1", "disposition": "ahead-only"},
    {"branch": "old/d", "sha": "d1", "disposition": "contained"},
]}
BASE = {"lint": "success", "unit": "success", "flaky": "failure"}


def test_feature_rows_select_ahead_and_diverged_only():
    rows = s.feature_rows(REG)
    assert [r["branch"] for r in rows] == ["feat/a-x", "feat/b-y", "fix/c"]
    assert {r["class"] for r in rows} == {"AHEAD", "DIVERGED"}


def test_vm_census_uppercase_classes_accepted():
    reg = {"records": [{"name": "x", "sha": "1", "class": "AHEAD"}, {"name": "y", "sha": "2", "class": "IN_MASTER"}]}
    assert [r["branch"] for r in s.feature_rows(reg)] == ["x"]


def test_missing_check_at_tip_is_regression():
    v = s.regression_verdict({"lint": "success"}, BASE)
    assert v["verdict"] == "regressed"
    assert v["regressed_checks"] == [{"check": "unit", "baseline": "success", "tip": "missing"}]


def test_baseline_failure_ignored_and_green():
    assert s.regression_verdict({"lint": "success", "unit": "success", "flaky": "failure"}, BASE)["verdict"] == "green"


def test_untestable_is_first_class():
    v = s.regression_verdict(None, BASE)
    assert v["verdict"] == "untestable" and v["reason"]


def test_perf_verdicts():
    assert s.perf_verdict(None) == "no-benchmark"
    assert s.perf_verdict({"t": {"baseline": 100, "tip": 130}}) == "regressed"
    assert s.perf_verdict({"t": {"baseline": 100, "tip": 70}}) == "improved"
    assert s.perf_verdict({"t": {"baseline": 100, "tip": 102}}) == "flat"


def test_overlap_components_union_shared_paths():
    comps = s.overlap_components({"a": ["x.py"], "b": ["x.py", "y.py"], "c": ["z.py"]})
    assert comps["a"] == comps["b"] != comps["c"]


def test_build_map_delta_and_tip_mismatch():
    checks = {"feat/a-x": {"tip_sha": "a1", "checks": {"lint": "success", "unit": "success"}},
              "feat/b-y": {"tip_sha": "OLD", "checks": {"lint": "success", "unit": "success"}}}
    prior = {"rows": [{"branch": "feat/a-x", "sha": "a1", "verdict": "regressed"}]}
    m = s.build_map(REG, checks, BASE, prior=prior, now="2026-11-18T00:00:00Z")
    by = {r["branch"]: r for r in m["rows"]}
    assert by["feat/a-x"]["verdict"] == "green" and by["feat/a-x"]["delta"] == "regressed→green"
    assert by["feat/b-y"]["verdict"] == "untestable"
    assert by["fix/c"]["verdict"] == "untestable" and by["fix/c"]["delta"] == "new"
    assert m["verdict_counts"] == {"green": 1, "untestable": 2}
    assert m["no_benchmark_share"] == 1.0
    assert m["policy"]["read_only"] is True


def test_build_map_deterministic():
    a = s.build_map(REG, {}, BASE, now="t")
    b = s.build_map(REG, {}, BASE, now="t")
    assert a == b
