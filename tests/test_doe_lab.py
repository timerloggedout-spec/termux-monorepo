"""ExperimentsLab runner (scripts/doe/lab_runner.py): plan
determinism + instance stamping, and the record loop (results ->
EXPERIMENT records + SUMMARY verdict) on synthetic results."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CAMP = ROOT / "experiments/doe/lab-1-prompt-x-model-x-role"


def _runner():
    spec = importlib.util.spec_from_file_location(
        "lab_runner", ROOT / "scripts/doe/lab_runner.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_plan_is_deterministic_and_instance_stamped():
    lr = _runner()
    p1, p2 = lr.build_plan(CAMP), lr.build_plan(CAMP)
    assert p1 == p2
    assert p1["planned_runs"] == 64 and p1["cells"] == 8
    keys = {r["instance"]["instance_key"] for r in p1["rows"]}
    assert len(keys) == 8  # one configured instance per cell
    for r in p1["rows"]:
        inst = r["instance"]
        assert inst["system_prompt"]["sha256"] == lr.IK.sha256_text(
            lr.composed_prompt(CAMP, r["factors"]["prompt"],
                               r["factors"]["role"]))


def test_record_loop_validates_and_selects(tmp_path):
    lr = _runner()
    camp = tmp_path / "lab-1"
    shutil.copytree(CAMP, camp)
    plan = lr.build_plan(camp)
    lines = []
    def recovered(f):
        if f["prompt"] == "prompt-b":
            return 1
        if "gpt" in f["model"]:
            return 4 if f["role"] == "reviewer" else 3
        return 2
    for r in plan["rows"]:
        lines.append(json.dumps({
            "cell": r["cell"], "task": r["task"],
            "recovered": recovered(r["factors"]), "required": 4,
            "input_tokens": 100, "elapsed_ms": 5,
            "observed_at": "2026-10-30T00:00:00Z"}))
    res = tmp_path / "results.jsonl"
    res.write_text("\n".join(lines) + "\n")
    summary = lr.record(camp, res)
    assert summary["runs"] == 64
    assert summary["verdict"].startswith("selected: c")
    assert summary["main_effects"]["prompt[prompt-b-prompt-a]"] < 0  # prompt-a stronger
    schema = json.loads(
        (ROOT / "docs/ops/corpus/EXPERIMENT.schema.json").read_text())
    recs = list((camp / "records").glob("*.json"))
    assert len(recs) == 64
    for rp in recs:
        jsonschema.validate(json.loads(rp.read_text()), schema)
