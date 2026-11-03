"""Speculators token strategies (scripts/speculators/): registry
completeness against the fork's model tree, plan determinism +
instance stamping, and the record loop (metrics, selection, and
the lossless gate that disqualifies any cell whose outputs differ
from verifier-only decoding)."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMP = ROOT / "experiments/speculators/token-strategies"

# Model dirs in timerloggedout-spec/speculators_fork
# @ c13304cf3ec2, src/speculators/models/ (read firsthand).
FORK_MODEL_DIRS = {"dflash", "dspark", "eagle3", "mtp", "peagle"}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _strategies():
    return _load("strategies", ROOT / "scripts/speculators/strategies.py")


def _evaluate():
    return _load("evaluate", ROOT / "scripts/speculators/evaluate.py")


def test_registry_covers_fork_models_plus_baseline():
    st = _strategies()
    assert set(st.speculative_ids()) == FORK_MODEL_DIRS
    for sid in st.speculative_ids():
        entry = st.STRATEGIES[sid]
        assert entry["fork_module"] == f"src/speculators/models/{sid}"
        assert entry["fork_docs"] == (
            f"docs/user_guide/algorithms/{sid}.md")
        assert entry["lossless"] is True
    assert st.STRATEGIES["baseline"]["fork_module"] is None
    assert st.FORK_REF == "c13304cf3ec212171c7ad536f18698a7c67f18a8"


def test_plan_is_deterministic_and_instance_stamped():
    ev = _evaluate()
    p1, p2 = ev.build_plan(CAMP), ev.build_plan(CAMP)
    assert p1 == p2
    assert p1["cells"] == 12 and p1["planned_runs"] == 48
    keys = {r["instance"]["instance_key"] for r in p1["rows"]}
    assert len(keys) == 12  # one configured instance per cell
    for r in p1["rows"]:
        inst = r["instance"]
        assert inst["system_prompt"]["sha256"] == ev.IK.sha256_text(
            ev.strategy_prompt(r["factors"]["strategy"]))
        assert inst["model"] == (
            f"{r['factors']['verifier']}+{r['factors']['strategy']}")


def _results(plan, speed: dict[str, float], *,
             violate: str | None = None) -> list[str]:
    lines = []
    for r in plan["rows"]:
        strat = r["factors"]["strategy"]
        s = speed[strat]
        lines.append(json.dumps({
            "cell": r["cell"], "task": r["task"],
            "steps": 10, "drafted": 40,
            "accepted": 30 if strat != "baseline" else 0,
            "elapsed_ms": 100.0 / s, "baseline_elapsed_ms": 100.0,
            "output_match": not (violate == strat)}))
    return lines


def test_record_emits_experiment_records(tmp_path):
    ev = _evaluate()
    camp = tmp_path / "camp"
    shutil.copytree(CAMP, camp)
    plan = ev.build_plan(camp)
    speed = {"baseline": 1.0, "eagle3": 1.3, "peagle": 1.6,
             "dflash": 1.5, "dspark": 1.45, "mtp": 1.25}
    res = tmp_path / "results.jsonl"
    res.write_text("\n".join(_results(plan, speed)) + "\n")
    ev.record(camp, res)
    import jsonschema
    schema = json.loads(
        (ROOT / "docs/ops/corpus/EXPERIMENT.schema.json").read_text())
    recs = list((camp / "records").glob("*.json"))
    assert len(recs) == 48
    for rp in recs:
        rec = json.loads(rp.read_text())
        jsonschema.validate(rec, schema)
        assert rec["treatment"]["instance"]["instance_key"]
        assert rec["metrics"]["lossless_violation"] == 0


def test_provider_phrases_change_instance(tmp_path):
    ev = _evaluate()
    camp = tmp_path / "camp"
    shutil.copytree(CAMP, camp)
    base = ev.build_plan(camp)
    design = json.loads((camp / "DESIGN.json").read_text())
    design["provider_phrases"] = {"Qwen/Qwen3-8B": {
        "prefix": "Build the Future Now. Make it so.",
        "suffix": "Show me what you got. GB"}}
    (camp / "DESIGN.json").write_text(json.dumps(design))
    phrased = ev.build_plan(camp)
    b = {r["run_id"]: r for r in base["rows"]}
    for r in phrased["rows"]:
        inst = r["instance"]
        if r["factors"]["verifier"] == "Qwen/Qwen3-8B":
            assert inst["instance_key"] != (
                b[r["run_id"]]["instance"]["instance_key"])
            assert "(+ provider phrases)" in (
                inst["system_prompt"]["ref"])
            composed = ("Build the Future Now. Make it so.\n\n"
                        + ev.strategy_prompt(r["factors"]["strategy"])
                        + "\n\nShow me what you got. GB")
            assert inst["system_prompt"]["sha256"] == (
                ev.IK.sha256_text(composed))
        else:
            assert inst == b[r["run_id"]]["instance"]


def test_record_selects_fastest_qualified(tmp_path):
    ev = _evaluate()
    camp = tmp_path / "camp"
    shutil.copytree(CAMP, camp)
    plan = ev.build_plan(camp)
    speed = {"baseline": 1.0, "eagle3": 1.3, "peagle": 1.6,
             "dflash": 1.5, "dspark": 1.45, "mtp": 1.25}
    res = tmp_path / "results.jsonl"
    res.write_text("\n".join(_results(plan, speed)) + "\n")
    summary = ev.record(camp, res)
    assert summary["runs"] == 48
    top = summary["verdict"]
    assert top.startswith("selected: ")
    cell = summary["cells"][top.split(": ")[1]]
    assert cell["strategy"] == "peagle"
    assert cell["acceptance_rate"] == 0.75
    assert cell["mean_accepted_length"] == 3.0
    assert abs(cell["mean_speedup"] - 1.6) < 1e-9


def test_record_lossless_gate_disqualifies(tmp_path):
    ev = _evaluate()
    camp = tmp_path / "camp"
    shutil.copytree(CAMP, camp)
    plan = ev.build_plan(camp)
    speed = {"baseline": 1.0, "eagle3": 1.3, "peagle": 1.6,
             "dflash": 1.5, "dspark": 1.35, "mtp": 1.25}
    res = tmp_path / "results.jsonl"
    res.write_text(
        "\n".join(_results(plan, speed, violate="peagle")) + "\n")
    summary = ev.record(camp, res)
    assert summary["verdict"].startswith("selected: ")
    bad = [c for c in summary["cells"].values()
           if c["strategy"] == "peagle"]
    assert all(c["lossless_violations"] == 4 for c in bad)
    cell = summary["cells"][summary["verdict"].split(": ")[1]]
    assert cell["strategy"] == "dflash"  # next fastest qualified
