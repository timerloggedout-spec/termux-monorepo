#!/usr/bin/env python3
"""Pilot 1 runner — DoE family campaign #1849 (issue #1865).

Executes the blocked 2x2 full factorial from DESIGN.json (routing x
representation) over the design's 8 predeclared source-grounded tasks,
offline and deterministically, and writes:

- records/<arm>-<task>.json — one EXPERIMENT.schema.json-conforming
  record per run (the family-adopted record schema), and
- SUMMARY.json — per-arm aggregates + factorial effects on accuracy +
  the verdict against the design's predeclared threshold.

Arms:
- routing=icm-guided: context is the task's target doc (the document
  the ICM map routes to).
- routing=bounded-search: keyword grep over docs/**/*.md +
  .agents/skills/**/*.md, ranked by keyword hits; top-1 doc wins.
- representation=explicit: context as retrieved.
- representation=compressed: context round-tripped through CedrLang
  compress -> expand (the module's natural-language path: symbol
  substitution + stopword removal; lossy by design — the loss is the
  measured effect); input tokens counted on the compressed form
  actually fed to the extractor.

Extraction: the 3 densest keyword-bearing windows (+/-8 lines around
keyword-bearing lines, ranked by keyword hits, disjoint); if
accuracy < 1.0, one fallback re-retrieval with 6 windows (rework).
Accuracy = required fragments recovered / required (case-insensitive).

Re-running regenerates records; observed_at / elapsed_ms are run
stamps. Everything else is deterministic at DESIGN.json's base_sha.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMP = ROOT / "experiments" / "doe" / "pilot-1-context-routing-x-compression"
sys.path.insert(0, str(ROOT / "deepcli"))
from deepcli.observatory.doe import full_factorial  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "cedrlang", ROOT / "workspace/compression_sandbox/cedrlang/cedrlang.py")
cedr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cedr)


def _corpus() -> list[Path]:
    docs = sorted((ROOT / "docs").rglob("*.md"))
    skills = sorted((ROOT / ".agents/skills").rglob("*.md"))
    return docs + skills


def _bounded_search(task: dict) -> Path:
    """Rank by distinct keywords present, tie-break by keyword density
    (hits per token) so long documents do not win on bulk alone."""
    best, best_key = None, None
    for path in _corpus():
        try:
            text = path.read_text(errors="replace").lower()
        except OSError:
            continue
        hits = [text.count(k.lower()) for k in task["keywords"]]
        distinct = sum(1 for h in hits if h > 0)
        density = sum(hits) / max(1, len(text.split()))
        key = (distinct, round(density, 6))
        if best_key is None or key > best_key:
            best, best_key = path, key
    return best


def _extract(context: str, task: dict, n_windows: int,
             half_window: int = 8) -> str:
    lines = context.splitlines()
    kw = [k.lower() for k in task["keywords"]]
    scored = []
    for i, line in enumerate(lines):
        hits = sum(1 for k in kw if k in line.lower())
        if hits:
            lo = max(0, i - half_window)
            hi = min(len(lines), i + half_window + 1)
            window_hits = sum(
                sum(1 for k in kw if k in lines[j].lower())
                for j in range(lo, hi))
            scored.append((window_hits, i, lo, hi))
    scored.sort(reverse=True)
    chosen = []
    for _hits, _i, lo, hi in scored:
        if all(hi <= c_lo or lo >= c_hi for c_lo, c_hi in chosen):
            chosen.append((lo, hi))
        if len(chosen) >= n_windows:
            break
    chosen.sort()
    return "\n".join("\n".join(lines[lo:hi]) for lo, hi in chosen)


def _accuracy(answer: str, task: dict) -> float:
    low = answer.lower()
    hits = sum(1 for f in task["required_fragments"] if f.lower() in low)
    return hits / len(task["required_fragments"])


def run() -> dict:
    design = json.loads((CAMP / "DESIGN.json").read_text())
    base_sha = design["base_sha"]
    arms = full_factorial(design["factors"])
    records_dir = CAMP / "records"
    records_dir.mkdir(exist_ok=True)
    for old in records_dir.glob("*.json"):
        old.unlink()
    observed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    per_arm: dict[str, list] = {}
    for arm in arms:
        arm_key = f"{arm['routing']}/{arm['representation']}"
        per_arm[arm_key] = []
        for task in design["tasks"]:
            t0 = time.perf_counter()
            if arm["routing"] == "icm-guided":
                doc_path = ROOT / task["target"]
            else:
                doc_path = _bounded_search(task)
            raw = doc_path.read_text(errors="replace")
            if arm["representation"] == "compressed":
                fed = cedr.compress(raw)
                context = cedr.expand(fed)
            else:
                fed = raw
                context = raw
            input_tokens = cedr.count_tokens(fed)
            answer = _extract(context, task, 3)
            acc = _accuracy(answer, task)
            rework = 0
            if acc < 1.0:
                rework = 1
                answer2 = _extract(context, task, 6)
                acc = max(acc, _accuracy(answer2, task))
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
            status = "passed" if acc >= 1.0 else "observed"
            rec = {
                "schema_version": "1.0",
                "experiment_id": (
                    f"doe-pilot-1-{arm['routing']}-{arm['representation']}"
                    f"-{task['id']}"),
                "observed_at": observed_at,
                "baseline_sha": base_sha,
                "candidate_sha": base_sha,
                "merge_base_sha": None,
                "suite": "doe-family:pilot-1-context-routing-x-compression",
                "cohort": f"{task['family']}/{task['stratum']}",
                "treatment": {
                    "manager_policy_id": "doe-expert/pilot-1-runner/v1",
                    "provider": None,
                    "model": None,
                    "arm": arm_key,
                },
                "status": status,
                "outcome": (
                    f"accuracy={acc:.3f} task={task['id']} "
                    f"retrieved={doc_path.relative_to(ROOT)} "
                    f"target={task['target']}"),
                "metrics": {
                    "accuracy": round(acc, 4),
                    "input_tokens": input_tokens,
                    "elapsed_ms": elapsed_ms,
                    "rework": rework,
                },
                "provenance": "manual",
                "confidence": "high",
                "evidence_refs": [
                    "https://github.com/timerloggedout-spec/termux-monorepo"
                    "/blob/master/experiments/doe/"
                    "pilot-1-context-routing-x-compression/DESIGN.json",
                ],
            }
            name = f"{arm['routing']}-{arm['representation']}-{task['id']}.json"
            (records_dir / name).write_text(json.dumps(rec, indent=1) + "\n")
            per_arm[arm_key].append(rec)
    import statistics as _stats
    arm_summary = {}
    for arm_key, recs in per_arm.items():
        n = len(recs)
        arm_summary[arm_key] = {
            "runs": n,
            "mean_accuracy": round(
                sum(r["metrics"]["accuracy"] for r in recs) / n, 4),
            "accuracy_sd": round(_stats.stdev(
                [r["metrics"]["accuracy"] for r in recs]), 4) if n > 1 else 0.0,
            "mean_input_tokens": round(
                sum(r["metrics"]["input_tokens"] for r in recs) / n, 1),
            "mean_elapsed_ms": round(
                sum(r["metrics"]["elapsed_ms"] for r in recs) / n, 3),
            "total_rework": sum(r["metrics"]["rework"] for r in recs),
        }
    ig_e = arm_summary["icm-guided/explicit"]["mean_accuracy"]
    ig_c = arm_summary["icm-guided/compressed"]["mean_accuracy"]
    bs_e = arm_summary["bounded-search/explicit"]["mean_accuracy"]
    bs_c = arm_summary["bounded-search/compressed"]["mean_accuracy"]
    effects = {
        "routing_main_effect": round(
            ((ig_e + ig_c) - (bs_e + bs_c)) / 2, 4),
        "representation_main_effect": round(
            ((ig_c + bs_c) - (ig_e + bs_e)) / 2, 4),
        "interaction": round(((ig_c - ig_e) - (bs_c - bs_e)) / 2, 4),
    }
    explicit_acc = (ig_e + bs_e) / 2
    compressed_acc = (ig_c + bs_c) / 2
    explicit_tok = (arm_summary["icm-guided/explicit"]["mean_input_tokens"]
                    + arm_summary["bounded-search/explicit"]
                    ["mean_input_tokens"]) / 2
    compressed_tok = (arm_summary["icm-guided/compressed"]
                      ["mean_input_tokens"]
                      + arm_summary["bounded-search/compressed"]
                      ["mean_input_tokens"]) / 2
    ok = (explicit_acc - compressed_acc) <= 0.10 and compressed_tok < explicit_tok
    summary = {
        "campaign_id": design["campaign_id"],
        "base_sha": base_sha,
        "generated_at": observed_at,
        "runs": sum(a["runs"] for a in arm_summary.values()),
        "arms": arm_summary,
        "effects_accuracy": effects,
        "predeclared_threshold": design["hypothesis"][
            "predeclared_threshold"],
        "verdict": "threshold_met" if ok else "threshold_not_met",
    }
    (CAMP / "SUMMARY.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


if __name__ == "__main__":
    s = run()
    print(json.dumps(s, indent=1))
