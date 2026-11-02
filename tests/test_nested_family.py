#!/usr/bin/env python3
"""Tests for scripts/tracking/nested_family.py — control-type, minimal.

Run: python3 -m pytest tests/test_nested_family.py -q  OR  python3 tests/test_nested_family.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "tracking"))
from nested_family import build  # noqa: E402

STAMP = {
    "dispatch_id": "cert-unit-1", "ts": "2026-11-01T00:00:00Z",
    "provider": "sealion", "model": "aisingapore/Llama-SEA-LION-v3-70B-IT",
    "moniker": "optimizations-assurance", "role": "builder",
    "context": "FCC L1 unit", "task_class": "certifications-unit",
    "run": {"run_id": 111, "session_id": None, "workflow": "cert-unit.yml"},
    "outcome": {"status": "completed", "gate_call": "PASS", "confirmed": None},
}

RECORD = {
    "experiment_id": "routed-dispatch", "status": "passed", "origin": "live",
    "observed_at": "2026-11-01T01:00:00Z", "session_id": None,
    "treatment": {"provider": "sealion", "model": STAMP["model"],
                  "instance": {"provider": "sealion", "model": STAMP["model"],
                               "role": "builder", "moniker": "optimizations-assurance",
                               "context": "FCC L1 M5 theory batch",
                               "instance_key": "7e20822af41d"}},
    "metrics": {"task_class": None, "first_pass_success": True, "pr": None},
    # task_class/workflow/run_id/gate_call absent: the stamp enriches them
}


def _tree() -> Path:
    # sandbox-local temp (tempfile module has no usable dir in this VM)
    base = Path(__file__).resolve().parent / ".tmp-nested-family"
    import shutil
    shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True)
    sdir = base / "experiments" / "doe" / "routed-dispatch" / "stamps"
    sdir.mkdir(parents=True)
    (sdir / "cert-unit-1.json").write_text(json.dumps(STAMP))
    stamp2 = dict(STAMP, dispatch_id="invoke-3", provider="baseten", model=None,
                  task_class="inference-invoke",
                  run={"run_id": 333, "session_id": None, "workflow": "provider-invoke.yml"})
    (sdir / "invoke-3.json").write_text(json.dumps(stamp2))
    rdir = base / "experiments" / "doe" / "routed-dispatch" / "records"
    rdir.mkdir(parents=True)
    (rdir / "cert-unit-1.json").write_text(json.dumps(RECORD))  # same dispatch as STAMP: record wins, stamp enriches
    (base / "ops" / "3l0").mkdir(parents=True)
    intake = dict(STAMP)  # same dispatch via fan-out: must dedupe
    extra = dict(STAMP, dispatch_id="provider-invoke-2", provider="mistral",
                 model="mistral-small-latest", task_class="inference-invoke",
                 run={"run_id": "222", "session_id": None, "workflow": "provider-invoke.yml"})
    (base / "ops" / "3l0" / "intake.jsonl").write_text(
        json.dumps(intake) + "\n" + json.dumps(extra) + "\n")
    (base / "ops" / "challenge").mkdir(parents=True)
    desk = {"traversals": [
        {"entry": "routed-dispatch", "provider_usage": [
            {"provider": "sealion", "model": STAMP["model"], "session_id": "s-dup",
             "state": "landed (merged 2c0894d2e7d3; synced f7270f379fae)"}]},  # prose state: bucketed in summary, verbatim in task
        {"entry": "D1", "provider_usage": [
            {"provider": "jules", "model": "NOT_ESTABLISHED", "role": "builder",
             "moniker": "challenge-entries", "session_id": "sess-9", "state": "landed"}]},
    ]}
    (base / "ops" / "challenge" / "desk-feed.json").write_text(json.dumps(desk))
    return base


def test_nesting_and_dedupe():
    feed = build(_tree())
    assert feed["schema"] == "nested-family/v1"
    assert feed["summary"]["providers"] == 4  # sealion, mistral, jules, baseten
    assert feed["summary"]["tasks"] == 5      # record + stamp-only + intake-extra + 2 desk rows
    assert feed["summary"]["dispatches"] == 3
    by_src = feed["summary"]["by_source"]
    assert by_src == {"records": 1, "stamps": 1, "intake": 1, "desk-usage": 2}
    assert feed["summary"]["by_outcome"] == {
        "passed": 1, "completed": 2, "landed": 1, "(prose state — verbatim in tasks)": 1}
    baseten = next(p for p in feed["providers"] if p["provider"] == "baseten")
    assert baseten["models"][0]["model"] == "NOT_ESTABLISHED"  # null model, literal bucket
    sealion = next(p for p in feed["providers"] if p["provider"] == "sealion")
    model = sealion["models"][0]
    assert model["roles"] == ["builder"]
    task = next(t for t in model["tasks"] if t["source"] == "records")
    assert task["run_id"] == 111 and task["dispatch_id"] == "cert-unit-1"  # run_id enriched from stamp
    assert task["source_ref"].endswith("records/cert-unit-1.json")
    assert task["instance_key"] == "7e20822af41d" and task["first_pass"] is True
    assert task["task_class"] == "certifications-unit"  # enriched from stamp
    assert task["outcome"] == {"status": "passed", "gate_call": "PASS", "confirmed": None}


def test_not_established_model_stays_literal():
    feed = build(_tree())
    jules = next(p for p in feed["providers"] if p["provider"] == "jules")
    assert jules["models"][0]["model"] == "NOT_ESTABLISHED"
    t = jules["models"][0]["tasks"][0]
    assert t["dispatch_id"] is None and t["session_id"] == "sess-9"
    assert t["outcome"]["status"] == "landed"
    assert any("desk-usage" in g for g in feed["gaps"])


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
    print("all tests passed")
