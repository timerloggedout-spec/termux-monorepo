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


def test_provider_phrases_compose_into_prompt_and_key():
    LR = _runner()
    design = json.loads((CAMP / "DESIGN.json").read_text())
    cell = {"prompt": "prompt-a", "model": "openrouter/openai/gpt-4o-mini",
            "role": "triage"}
    base = LR.cell_instance(CAMP, design, cell)
    design2 = dict(design)
    design2["provider_phrases"] = {
        "openrouter/openai/gpt-4o-mini": {
            "prefix": "Build the Future Now. Make it so.",
            "suffix": "Show me what you got. GB"}}
    phrased = LR.cell_instance(CAMP, design2, cell)
    assert phrased["instance_key"] != base["instance_key"]
    assert "provider phrases" in phrased["system_prompt"]["ref"]
    text = LR.composed_prompt(
        CAMP, "prompt-a", "triage",
        design2["provider_phrases"]["openrouter/openai/gpt-4o-mini"])
    assert text.startswith("Build the Future Now. Make it so.")
    assert text.endswith("Show me what you got. GB")


def test_phrase_layer_wiring_changes_instance(tmp_path):
    LR = _runner()
    fixture = tmp_path / "phrases.json"
    fixture.write_text(json.dumps({"providers": {"deepseek": {
        "match": ["deepseek"], "prefixes": ["PRE "],
        "suffixes": ["Build the Future Now. Make it so."]}}}))
    design = json.loads((CAMP / "DESIGN.json").read_text())
    cell = {"prompt": "prompt-a", "model": "openrouter/deepseek/x",
            "role": "triage"}
    plain = LR.cell_instance(CAMP, design, cell)
    design2 = dict(design)
    design2["phrase_layer"] = {"phrases_file": str(fixture)}
    layered = LR.cell_instance(CAMP, design2, cell)
    assert layered["instance_key"] != plain["instance_key"]
    assert "phrase layer: deepseek/prefix+suffix/verbatim" in \
        layered["system_prompt"]["ref"]
