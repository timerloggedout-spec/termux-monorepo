#!/usr/bin/env python3
"""ExperimentsLab runner — live DoE campaigns over configured instances.

The entire repo is the experiment floor; this runner is the lab
instrument for DELIBERATE campaigns. It composes what already
exists: doe.py generators (design), the configured-instance
identity (scripts/doe/instance_key.py), and the EXPERIMENT record
schema (one run = one record).

Modes:
  plan    DESIGN.json -> PLAN.json: factorial cells (doe.py
          full_factorial over the design's factors) x tasks; every
          row carries its full treatment.instance + instance_key.
          Deterministic; consumes no quota.
  record  results.jsonl (one JSON object per executed run:
          {cell, task, recovered, required, input_tokens,
          elapsed_ms}) -> records/*.json (EXPERIMENT-conforming) +
          SUMMARY.json (per-cell means, main effects — descriptive
          only — and the verdict vs the design's pre-registered
          threshold).

Execution itself rides the fleet's provider lanes (free routes
only, per the campaign's quota note); this runner never dispatches.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "deepcli"))
from deepcli.observatory.doe import full_factorial  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "instance_key", Path(__file__).with_name("instance_key.py"))
IK = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IK)

ROLE_LINES = {
    "triage": "Role: triage — classify the task first, then extract.",
    "reviewer": "Role: reviewer — verify every fragment against the "
                "source text before returning it.",
}
TOOLS = ["retrieve_context", "extract_fragments"]


def composed_prompt(campaign_dir: Path, prompt_level: str,
                    role: str, phrases: dict | None = None) -> str:
    text = (campaign_dir / "prompts" /
            f"{prompt_level}.md").read_text().strip()
    parts = []
    if phrases and phrases.get("prefix"):
        parts.append(phrases["prefix"].strip())
    parts.append(text)
    parts.append(ROLE_LINES[role])
    if phrases and phrases.get("suffix"):
        parts.append(phrases["suffix"].strip())
    return "\n\n".join(parts)


def cell_instance(campaign_dir: Path, design: dict, cell: dict) -> dict:
    # Mandatory provider phrases (owner order, 2026-10-31): when the
    # campaign design declares provider_phrases for this model route
    # (verbatim from the harmony_hub prompt sources), they are composed
    # INTO the dispatched prompt and covered by its hash — a run
    # without them is a different configured instance.
    phrases = (design.get("provider_phrases") or {}).get(cell["model"])
    prompt_text = composed_prompt(campaign_dir, cell["prompt"],
                                  cell["role"], phrases)
    phrase_stamp = None
    layer_cfg = design.get("phrase_layer")
    if layer_cfg and not phrases:
        # JIT phrase layer (owner, 2026-10-31): sets come from the
        # provider-phrases SSOT (ops/phrases submodule). Enabled in
        # the design but data not checked out = fail loud at plan
        # time, never a silent unphrased dispatch.
        _ps = importlib.util.spec_from_file_location(
            "phrase_layer", Path(__file__).parent / "phrase_layer.py")
        PL = importlib.util.module_from_spec(_ps)
        _ps.loader.exec_module(PL)
        pfile = layer_cfg.get("phrases_file") or str(
            campaign_dir.parents[2] / "ops" / "phrases" /
            "phrases.json")
        data = PL.load_sets(pfile)
        prompt_text, phrase_stamp = PL.apply_phrases(
            prompt_text, data, cell["model"],
            selection=layer_cfg.get("selection", "first"),
            placement=layer_cfg.get("placement", "prefix+suffix"),
            form=layer_cfg.get("form", "verbatim"),
            profile=layer_cfg.get("profile"),
            token_forms=layer_cfg.get("token_forms"))
    provider, model = cell["model"].split("/", 1)
    p_sha = IK.sha256_text(prompt_text)
    t_sha = IK.tools_sha256(TOOLS)
    key = IK.instance_key(
        provider=provider, model=model, system_prompt_sha256=p_sha,
        tools_sha256_=t_sha, role=cell["role"],
        moniker=design.get("moniker", "doe-expert"),
        context=design["campaign_id"])
    return {
        "provider": provider, "model": model,
        "system_prompt": {
            "ref": f"experiments/doe/{design['campaign_id']}/prompts/"
                   f"{cell['prompt']}.md (+ role line: {cell['role']})"
                   + (" (+ provider phrases)"
                      if phrases else "")
                   + (f" (+ phrase layer: {phrase_stamp['provider']}/"
                      f"{phrase_stamp['placement']}/"
                      f"{phrase_stamp['form']}"
                      + (f"/{phrase_stamp['profile']}"
                         if phrase_stamp["profile"] else "") + ")"
                      if phrase_stamp else ""),
            "sha256": p_sha},
        "tools": {"ref": "tools:doe-expert:lab-runner",
                  "sha256": t_sha},
        "role": cell["role"],
        "moniker": design.get("moniker", "doe-expert"),
        "context": design["campaign_id"],
        "instance_key": key,
    }


def build_plan(campaign_dir: Path) -> dict:
    design = json.loads((campaign_dir / "DESIGN.json").read_text())
    cells = full_factorial(design["factors"])
    rows = []
    for ci, cell in enumerate(cells):
        cell_id = f"c{ci + 1:02d}"
        inst = cell_instance(campaign_dir, design, cell)
        for task in design["tasks"]:
            rows.append({
                "run_id": f"{design['campaign_id']}-{cell_id}-{task['id']}",
                "cell": cell_id, "factors": cell, "task": task["id"],
                "instance": inst,
            })
    return {"campaign_id": design["campaign_id"],
            "design_type": design["design"]["type"],
            "cells": len(cells), "tasks": len(design["tasks"]),
            "planned_runs": len(rows), "rows": rows}


def record(campaign_dir: Path, results_path: Path) -> dict:
    design = json.loads((campaign_dir / "DESIGN.json").read_text())
    plan = build_plan(campaign_dir)
    by_run = {r["run_id"]: r for r in plan["rows"]}
    records_dir = campaign_dir / "records"
    records_dir.mkdir(exist_ok=True)
    per_cell: dict[str, list[float]] = {}
    n = 0
    for line in results_path.read_text().splitlines():
        if not line.strip():
            continue
        res = json.loads(line)
        run_id = (f"{design['campaign_id']}-{res['cell']}-"
                  f"{res['task']}")
        row = by_run[run_id]
        acc = res["recovered"] / res["required"] if res["required"] \
            else 0.0
        per_cell.setdefault(res["cell"], []).append(acc)
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
            "outcome": f"accuracy {acc:.3f} "
                       f"({res['recovered']}/{res['required']} fragments)",
            "metrics": {"accuracy": round(acc, 4),
                        "input_tokens": res.get("input_tokens"),
                        "elapsed_ms": res.get("elapsed_ms")},
            "provenance": "other",
            "confidence": "high",
        }
        (records_dir / f"{run_id}.json").write_text(
            json.dumps(rec, indent=1) + "\n")
        n += 1
    cell_means = {c: round(sum(v) / len(v), 4)
                  for c, v in sorted(per_cell.items())}
    cells = {r["cell"]: r["factors"] for r in plan["rows"]}
    effects = {}
    for factor in design["factors"]:
        levels = design["factors"][factor]
        if len(levels) == 2:
            hi = [cell_means[c] for c in cell_means
                  if cells[c][factor] == levels[1]]
            lo = [cell_means[c] for c in cell_means
                  if cells[c][factor] == levels[0]]
            if hi and lo:
                # Named contrast: levels[1] minus levels[0], so the
                # sign is self-describing (pilot-1 SUMMARY style).
                effects[f"{factor}[{levels[1]}-{levels[0]}]"] = round(
                    sum(hi) / len(hi) - sum(lo) / len(lo), 4)
    ranked = sorted(cell_means.items(), key=lambda kv: -kv[1])
    thr = design["hypothesis"]["selection_rule"]
    verdict = "no_selection"
    if len(ranked) >= 2:
        top, second = ranked[0], ranked[1]
        if top[1] - second[1] >= thr["min_margin"] and \
                top[1] >= thr["min_accuracy"]:
            verdict = f"selected: {top[0]}"
    summary = {"campaign_id": design["campaign_id"], "runs": n,
               "cell_means": cell_means, "main_effects": effects,
               "ranked_cells": [c for c, _ in ranked],
               "verdict": verdict,
               "note": "Descriptive effects from records; live "
                       "campaign, designed + pre-registered."}
    (campaign_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=1) + "\n")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan", "record"])
    ap.add_argument("campaign", help="campaign directory")
    ap.add_argument("--results", help="results.jsonl (record mode)")
    a = ap.parse_args()
    cdir = Path(a.campaign)
    if a.mode == "plan":
        plan = build_plan(cdir)
        (cdir / "PLAN.json").write_text(
            json.dumps(plan, indent=1) + "\n")
        print(f"PLAN: {plan['cells']} cells x {plan['tasks']} tasks "
              f"= {plan['planned_runs']} runs")
    else:
        s = record(cdir, Path(a.results))
        print(f"SUMMARY: {s['runs']} runs, verdict {s['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
