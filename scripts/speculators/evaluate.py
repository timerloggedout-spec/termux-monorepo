#!/usr/bin/env python3
"""Speculators evaluation harness — multiple token strategies,
measured on one ruler.

Implements issue #195's evaluation surface for the strategies in
scripts/speculators/strategies.py (timerloggedout-spec/
speculators_fork @ c13304cf3ec2). Pattern follows the ExperimentsLab
runner (scripts/doe/lab_runner.py): plan is deterministic and
dispatches nothing; record turns executed results into metrics +
a verdict against the design's pre-registered selection rule.
Execution itself (training draft models in the fork, serving them
in vLLM) rides GPU/provider lanes; this harness never dispatches.

Modes:
  plan    DESIGN.json -> PLAN.json: strategies x verifiers
          factorial cells x tasks; every row carries its full
          treatment.instance (configured-instance identity,
          scripts/doe/instance_key.py) + instance_key. The
          instance's system_prompt is the strategy's canonical
          registry entry; its tools are the fork train + vLLM
          serve surfaces.
  record  results.jsonl (one JSON object per executed run:
          {cell, task, steps, drafted, accepted, elapsed_ms,
          baseline_elapsed_ms, output_match}) -> records/*.json
          (one EXPERIMENT-schema record per run, the DoE record
          of the run) + SUMMARY.json: per-cell acceptance rate,
          mean accepted length, speedup vs the run's own
          baseline timing, and the verdict. LOSSLESS GATE:
          speculative decoding is only valid while outputs
          match verifier-only decoding — any run with
          output_match != true disqualifies its cell from
          selection, whatever its speed.

DoE wiring (2026-11-02): this harness is a DoE family member
(docs/ops/DOE-FAMILY.md, Speculators mapping). Plans stamp the
configured-instance identity via scripts/doe/instance_key.py;
provider phrases follow the lab_runner rule — a design may
declare provider_phrases per verifier route (verbatim prefix/
suffix composed into the strategy prompt and covered by its
hash) or a phrase_layer block (JIT layer over the
provider-phrases SSOT, scripts/doe/phrase_layer.py; enabled but
data missing = fail loud at plan time). A phrased run is a
different configured instance from an unphrased one.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "strategies", Path(__file__).with_name("strategies.py"))
_ST = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ST)
STRATEGIES, strategy_ids = _ST.STRATEGIES, _ST.strategy_ids

_spec = importlib.util.spec_from_file_location(
    "instance_key", ROOT / "scripts/doe/instance_key.py")
IK = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IK)

TOOLS = ["speculators.train", "vllm.serve"]


def strategy_prompt(strategy_id: str) -> str:
    """Canonical strategy configuration text (the instance's
    system_prompt equivalent): the registry entry, verbatim."""
    return json.dumps(STRATEGIES[strategy_id], sort_keys=True,
                      separators=(",", ":"))


def composed_prompt(campaign_dir: Path, design: dict,
                    strategy_id: str, verifier: str) -> tuple:
    """Strategy prompt + provider phrases, lab_runner rule.

    provider_phrases declared per verifier route in the design
    are composed INTO the prompt (prefix/suffix) and covered by
    its hash; a phrase_layer block instead routes the prompt
    through the JIT phrase layer (SSOT ops/phrases submodule) —
    enabled but data missing fails loud here, at plan time.
    Returns (prompt_text, ref_annotation)."""
    text = strategy_prompt(strategy_id)
    phrases = (design.get("provider_phrases") or {}).get(verifier)
    if phrases:
        parts = []
        if phrases.get("prefix"):
            parts.append(phrases["prefix"].strip())
        parts.append(text)
        if phrases.get("suffix"):
            parts.append(phrases["suffix"].strip())
        return "\n\n".join(parts), " (+ provider phrases)"
    layer_cfg = design.get("phrase_layer")
    if layer_cfg:
        _ps = importlib.util.spec_from_file_location(
            "phrase_layer", ROOT / "scripts/doe/phrase_layer.py")
        PL = importlib.util.module_from_spec(_ps)
        _ps.loader.exec_module(PL)
        pfile = layer_cfg.get("phrases_file") or str(
            ROOT / "ops" / "phrases" / "phrases.json")
        data = PL.load_sets(pfile)
        text, stamp = PL.apply_phrases(
            text, data, verifier,
            selection=layer_cfg.get("selection", "first"),
            placement=layer_cfg.get("placement", "prefix+suffix"),
            form=layer_cfg.get("form", "verbatim"),
            profile=layer_cfg.get("profile"),
            token_forms=layer_cfg.get("token_forms"),
            transform_cfg=layer_cfg.get("transform"))
        if stamp:
            return text, (f" (+ phrase layer: {stamp['provider']}/"
                          f"{stamp['placement']}/{stamp['form']}"
                          + (f"/{stamp['profile']}"
                             if stamp["profile"] else "") + ")")
    return text, ""


def cell_instance(campaign_dir: Path, design: dict, strategy_id: str,
                  verifier: str) -> dict:
    prompt_text, annotation = composed_prompt(
        campaign_dir, design, strategy_id, verifier)
    p_sha = IK.sha256_text(prompt_text)
    t_sha = IK.tools_sha256(TOOLS)
    provider, model = "speculators_fork", f"{verifier}+{strategy_id}"
    key = IK.instance_key(
        provider=provider, model=model, system_prompt_sha256=p_sha,
        tools_sha256_=t_sha, role="evaluation",
        moniker=design.get("moniker", "speculators"),
        context=design["campaign_id"])
    return {
        "provider": provider, "model": model,
        "system_prompt": {
            "ref": f"scripts/speculators/strategies.py#{strategy_id}"
                   f"{annotation}",
            "sha256": p_sha},
        "tools": {"ref": "tools:speculators:evaluate",
                  "sha256": t_sha},
        "role": "evaluation",
        "moniker": design.get("moniker", "speculators"),
        "context": design["campaign_id"],
        "instance_key": key,
    }


def build_plan(campaign_dir: Path) -> dict:
    design = json.loads((campaign_dir / "DESIGN.json").read_text())
    cells = list(itertools.product(strategy_ids(),
                                   design["verifiers"]))
    rows = []
    cell_ids = {}
    for ci, (strategy_id, verifier) in enumerate(cells):
        cell_id = f"c{ci + 1:02d}"
        cell_ids[(strategy_id, verifier)] = cell_id
        inst = cell_instance(campaign_dir, design, strategy_id,
                             verifier)
        for task in design["tasks"]:
            rows.append({
                "run_id": f"{design['campaign_id']}-{cell_id}-"
                          f"{task['id']}",
                "cell": cell_id,
                "factors": {"strategy": strategy_id,
                            "verifier": verifier},
                "task": task["id"],
                "instance": inst,
            })
    return {"campaign_id": design["campaign_id"],
            "fork": design["fork"],
            "cells": len(cells), "tasks": len(design["tasks"]),
            "planned_runs": len(rows), "rows": rows}


def record(campaign_dir: Path, results_path: Path) -> dict:
    design = json.loads((campaign_dir / "DESIGN.json").read_text())
    plan = build_plan(campaign_dir)
    by_run = {r["run_id"]: r for r in plan["rows"]}
    records_dir = campaign_dir / "records"
    records_dir.mkdir(exist_ok=True)
    per_cell: dict[str, dict] = {}
    n = 0
    for line in results_path.read_text().splitlines():
        if not line.strip():
            continue
        res = json.loads(line)
        run_id = (f"{design['campaign_id']}-{res['cell']}-"
                  f"{res['task']}")
        row = by_run[run_id]
        cell = per_cell.setdefault(res["cell"], {
            "strategy": row["factors"]["strategy"],
            "verifier": row["factors"]["verifier"],
            "runs": 0, "drafted": 0, "accepted": 0, "steps": 0,
            "speedups": [], "lossless_violations": 0})
        cell["runs"] += 1
        cell["drafted"] += res["drafted"]
        cell["accepted"] += res["accepted"]
        cell["steps"] += res["steps"]
        if res["elapsed_ms"]:
            cell["speedups"].append(
                res["baseline_elapsed_ms"] / res["elapsed_ms"])
        if res.get("output_match") is not True:
            cell["lossless_violations"] += 1
        # One EXPERIMENT record per run (docs/ops/corpus/
        # EXPERIMENT.schema.json) — the DoE record of the run,
        # instance-stamped exactly as planned.
        acc = res["accepted"] / res["drafted"] if res["drafted"] \
            else 0.0
        speedup = (res["baseline_elapsed_ms"] / res["elapsed_ms"]
                   if res["elapsed_ms"] else 0.0)
        rec = {
            "schema_version": "1.0",
            "experiment_id": run_id,
            "observed_at": res.get("observed_at",
                                   "1970-01-01T00:00:00Z"),
            "baseline_sha": design["base_sha"],
            "candidate_sha": design["base_sha"],
            "suite": design["campaign_id"],
            "treatment": {
                "manager_policy_id": design["campaign_id"],
                "provider": row["instance"]["provider"],
                "model": row["instance"]["model"],
                "arm": res["cell"],
                "instance": row["instance"],
            },
            "status": "observed",
            "outcome": f"acceptance {acc:.3f} "
                       f"({res['accepted']}/{res['drafted']} tokens), "
                       f"speedup {speedup:.2f}x, "
                       f"output_match={res.get('output_match')}",
            "metrics": {
                "acceptance_rate": round(acc, 4),
                "mean_accepted_length": round(
                    res["accepted"] / res["steps"], 4)
                    if res["steps"] else 0.0,
                "speedup": round(speedup, 4),
                "drafted": res["drafted"],
                "accepted": res["accepted"],
                "steps": res["steps"],
                "elapsed_ms": res["elapsed_ms"],
                "baseline_elapsed_ms": res["baseline_elapsed_ms"],
                "lossless_violation": int(
                    res.get("output_match") is not True),
            },
            "provenance": "other",
            "confidence": "high",
        }
        (records_dir / f"{run_id}.json").write_text(
            json.dumps(rec, indent=1) + "\n")
        n += 1
    for cell in per_cell.values():
        cell["acceptance_rate"] = (
            cell["accepted"] / cell["drafted"] if cell["drafted"]
            else 0.0)
        cell["mean_accepted_length"] = (
            cell["accepted"] / cell["steps"] if cell["steps"]
            else 0.0)
        cell["mean_speedup"] = (
            sum(cell["speedups"]) / len(cell["speedups"])
            if cell["speedups"] else 0.0)
        del cell["speedups"]
    rule = design["hypothesis"]["selection_rule"]
    qualified = {
        cid: c for cid, c in per_cell.items()
        if c["strategy"] != "baseline"
        and c["lossless_violations"] == 0
        and c["acceptance_rate"] >= rule["min_acceptance_rate"]
        and c["mean_speedup"] >= rule["min_speedup"]}
    if qualified:
        ranked = sorted(qualified,
                        key=lambda cid: qualified[cid]["mean_speedup"],
                        reverse=True)
        top = ranked[0]
        others = [qualified[cid]["mean_speedup"] for cid in ranked[1:]
                  if qualified[cid]["strategy"]
                  != qualified[top]["strategy"]]
        margin = (qualified[top]["mean_speedup"] - max(others)
                  if others else qualified[top]["mean_speedup"])
        verdict = (f"selected: {top}"
                   if margin >= rule["min_margin"]
                   else "no_selection: margin below threshold")
    else:
        verdict = "no_selection: no qualified cell"
    summary = {"campaign_id": design["campaign_id"], "runs": n,
               "cells": per_cell, "verdict": verdict}
    (campaign_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True) + "\n")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["plan", "record"])
    ap.add_argument("campaign_dir", type=Path)
    ap.add_argument("results", type=Path, nargs="?")
    args = ap.parse_args()
    if args.mode == "plan":
        plan = build_plan(args.campaign_dir)
        (args.campaign_dir / "PLAN.json").write_text(
            json.dumps(plan, indent=1, sort_keys=True) + "\n")
        print(f"plan: {plan['cells']} cells x {plan['tasks']} tasks "
              f"= {plan['planned_runs']} runs")
    else:
        summary = record(args.campaign_dir, args.results)
        print(f"record: {summary['runs']} runs -> "
              f"{summary['verdict']}")


if __name__ == "__main__":
    main()
