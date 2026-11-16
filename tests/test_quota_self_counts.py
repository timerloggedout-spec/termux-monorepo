"""Self-count layer (owner ruling 2026-11-03): the tally counts only
the fleet's own recorded events (dispatch stamps deduped, wall
events, Actions corpus), stamps its method + blind spots, and the
planner's matching layer derives labeled heuristic flags from the
counts - never readings. Offline, fixture roots."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


tally = load_mod("quota_self_counts", "scripts/quota_self_counts.py")
planner = load_mod("quota_allocation_planner",
                   "scripts/quota_allocation_planner.py")


def _write(root, rel, obj):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))


def _fixture(tmp_path):
    _write(tmp_path, "ops/quota/rate-limit-events.json", {"events": [
        {"at": "2026-11-01T00:00:00Z", "bucket": "github.api.user_token",
         "class": "core-exhaustion"},
        {"at": "2026-11-02T00:00:00Z", "bucket": "github.api.user_token",
         "class": "secondary-403"}]})
    _write(tmp_path,
           "experiments/doe/routed-dispatch/stamps/s1.json",
           {"provider": "DeepSeek", "model": "m", "ts": "2026-11-01",
            "dispatch_id": "d1"})
    _write(tmp_path,
           "experiments/doe/routed-dispatch/stamps/s2.json",
           {"provider": "DeepSeek", "model": "m", "ts": "2026-11-02",
            "dispatch_id": "d1"})  # duplicate id - counted once
    _write(tmp_path,
           "experiments/doe/routed-dispatch/records/r1.json",
           {"provider": "Claude", "model": "m", "ts": "2026-11-01",
            "dispatch_id": "d2"})
    _write(tmp_path,
           "docs/ops/generated/actions-performance-reconstructed-"
           "2026-11-01.json",
           {"run_count": 100, "total_jobs": 140})
    return tmp_path


def test_tally_counts_own_events_only(tmp_path):
    doc = tally.build(_fixture(tmp_path))
    assert doc["schema"] == "quota-self-counts/v1"
    assert doc["providers"]["deepseek"]["dispatches"] == 1
    assert doc["providers"]["claude"]["dispatches"] == 1
    b = doc["buckets"]["github.api.user_token"]
    assert b["wall_events"] == 2
    assert b["by_class"] == {"core-exhaustion": 1, "secondary-403": 1}
    assert doc["services"]["github.actions"]["runs_total"] == 100
    assert "self-count" in doc["method"]
    # blind spots are named, not silently zero
    assert any("spend" in n for n in doc["coverage_notes"])


def _plan_inputs(self_counts):
    registry = {"services": [
        {"id": "deepseek.api", "provider": "DeepSeek", "lane": "model",
         "limit": None, "window": "n/a"}]}
    allocations = {"pools": [{
        "id": "deepseek", "services": ["deepseek.api"],
        "allocations": [{"focus": "winning", "pct": 100,
                         "mode": "standing"}],
        "slices": []}]}
    readings = {"readings": []}
    return planner.plan(registry, allocations, readings,
                        self_counts=self_counts)


def test_planner_matching_flags_from_counts():
    counts = {"generated_at": "2026-11-03T00:00:00Z",
              "providers": {"deepseek": {"dispatches": 3}},
              "buckets": {}, "services": {}}
    pool = _plan_inputs(counts)["pools"][0]
    assert pool["self_counts"]["method"] == "self-count"
    assert pool["self_counts"]["totals"]["dispatches"] == 3
    assert pool["matching"]["flag"] == "unmatched-activity"
    assert pool["matching"]["layer"] == "heuristic"
    # stranded stays NOT ESTABLISHED - counts never dress as readings
    assert pool["stranded"] is None


def test_planner_no_counts_is_no_data():
    pool = _plan_inputs(None)["pools"][0]
    assert pool["self_counts"] is None
    assert pool["matching"]["flag"] == "no-data"
