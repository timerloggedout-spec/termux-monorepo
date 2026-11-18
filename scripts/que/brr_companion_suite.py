#!/usr/bin/env python3
"""BRR companion regression suite (#5552) — differential verdicts + feature-progress map.

DO consume a Branch Reconciliation Registry (schema branch-reconciliation-registry/v1,
PR #5523; VM census rows with AHEAD/DIVERGED accepted too) as the work list.
DO compare each feature branch's check set at tip vs the master baseline:
  regressed  := ∃ check: baseline=success ∧ tip ∈ {failure, missing}
  green      := ∀ baseline-success checks: tip=success ∧ ∃ ≥1 check observed
  untestable := checks unavailable, skipped, neutral, or not tied to the registry tip
DO emit perf verdict {improved | regressed | flat | no-benchmark} only when a metric is comparable.
DO cluster rows deterministically: (class, feature family, file-overlap component, verdict×perf).
DO emit the feature-progress map with Δ vs the prior cycle (append-only artifact).
Authority: read-only — ¬ merge ∧ ¬ push ∧ ¬ close ∧ ¬ delete (BRR DO-04 preserved).

Usage:
  python3 scripts/que/brr_companion_suite.py --registry registry.json \
      --checks checks.json --baseline baseline.json [--prior prior-map.json] \
      [--files files.json] [--bench bench.json] --out map.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

SCHEMA = "brr-feature-progress-map/v1"
SUITE_VERSION = "brr-companion-suite v1"
FEATURE_CLASSES = {"ahead-only": "AHEAD", "diverged": "DIVERGED", "AHEAD": "AHEAD", "DIVERGED": "DIVERGED"}
PASS = {"success"}
NEUTRAL = {"skipped", "neutral"}
PERF_FLAT_BAND = 0.05


def feature_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows = registry.get("branches") or registry.get("records") or []
    out = []
    for row in rows:
        cls = FEATURE_CLASSES.get(str(row.get("disposition") or row.get("class") or ""))
        if not cls:
            continue
        out.append({"branch": row.get("branch") or row.get("name"), "sha": row.get("sha"), "class": cls,
                    "ahead": row.get("ahead_of_default", row.get("ahead")),
                    "behind": row.get("behind_default", row.get("behind")),
                    "pull_requests": [p.get("number") for p in row.get("pull_requests") or [] if p.get("number")]})
    return sorted(out, key=lambda r: str(r["branch"]))


def regression_verdict(tip: dict[str, str] | None, baseline: dict[str, str]) -> dict[str, Any]:
    if not tip:
        return {"verdict": "untestable", "reason": "no check results at tip", "regressed_checks": []}
    regressed, untestable = [], []
    for name, base_conclusion in sorted(baseline.items()):
        if base_conclusion not in PASS:
            continue
        tip_conclusion = tip.get(name)
        if tip_conclusion is None:
            regressed.append({"check": name, "baseline": base_conclusion, "tip": "missing"})
        elif tip_conclusion in NEUTRAL:
            untestable.append({"check": name, "baseline": base_conclusion, "tip": tip_conclusion})
        elif tip_conclusion not in PASS:
            regressed.append({"check": name, "baseline": base_conclusion, "tip": tip_conclusion})
    if regressed:
        return {"verdict": "regressed", "reason": f"{len(regressed)} pass→fail∨missing", "regressed_checks": regressed}
    if untestable:
        return {"verdict": "untestable", "reason": f"{len(untestable)} baseline-success checks did not execute successfully",
                "regressed_checks": [], "untestable_checks": untestable}
    if not any(v in PASS for v in tip.values()):
        return {"verdict": "untestable", "reason": "tip carries ∅ passing check", "regressed_checks": []}
    return {"verdict": "green", "reason": None, "regressed_checks": []}


def perf_verdict(bench: dict[str, Any] | None) -> str:
    """bench := {metric: {"baseline": x, "tip": y, "higher_is_better": bool}}."""
    if not bench:
        return "no-benchmark"
    worse = better = compared = 0
    for metric in bench.values():
        if not isinstance(metric, dict):
            continue
        base, tip = metric.get("baseline"), metric.get("tip")
        if (not isinstance(base, (int, float)) or isinstance(base, bool)
                or not isinstance(tip, (int, float)) or isinstance(tip, bool) or base == 0):
            continue
        compared += 1
        delta = (tip - base) / abs(base)
        if not metric.get("higher_is_better", False):
            delta = -delta
        if delta > PERF_FLAT_BAND:
            better += 1
        elif delta < -PERF_FLAT_BAND:
            worse += 1
    if compared == 0:
        return "no-benchmark"
    if worse:
        return "regressed"
    if better:
        return "improved"
    return "flat"


def feature_family(branch: str) -> str:
    head = str(branch).split("/", 1)
    if len(head) == 2:
        tail = head[1].split("-", 1)[0]
        return f"{head[0]}/{tail}"
    return str(branch).split("-", 1)[0]


def overlap_components(files: dict[str, list[str]]) -> dict[str, int]:
    """Union branches touching ∃ shared path ⇒ one conflict-risk component id."""
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner: dict[str, str] = {}
    for branch in sorted(files):
        find(branch)
        for path in files[branch]:
            if path in owner:
                parent[find(branch)] = find(owner[path])
            else:
                owner[path] = branch
    roots = sorted({find(b) for b in files})
    ids = {root: i for i, root in enumerate(roots)}
    return {b: ids[find(b)] for b in files}


def build_map(registry: dict[str, Any], checks: dict[str, Any], baseline: dict[str, str],
              prior: dict[str, Any] | None = None, files: dict[str, list[str]] | None = None,
              bench: dict[str, Any] | None = None, now: str | None = None) -> dict[str, Any]:
    files = files or {}
    bench = bench or {}
    comps = overlap_components(files)
    prior_rows = {r["branch"]: r for r in (prior or {}).get("rows", [])}
    rows = []
    for feat in feature_rows(registry):
        branch = feat["branch"]
        tip_entry = checks.get(branch)
        tip_checks = tip_entry.get("checks") if isinstance(tip_entry, dict) else None
        if not isinstance(tip_entry, dict) or not feat.get("sha") or not tip_entry.get("tip_sha"):
            v = {"verdict": "untestable", "reason": "check evidence missing registry-tip SHA binding",
                 "regressed_checks": []}
        elif tip_entry["tip_sha"] != feat["sha"]:
            v = {"verdict": "untestable", "reason": "check results ≠ registry tip sha", "regressed_checks": []}
        else:
            v = regression_verdict(tip_checks, baseline)
        perf = perf_verdict(bench.get(branch))
        family = feature_family(branch)
        comp = comps.get(branch)
        before = prior_rows.get(branch)
        if before is None:
            delta = "new"
        elif before.get("sha") != feat["sha"]:
            delta = f"tip-moved:{before.get('verdict')}→{v['verdict']}"
        elif before.get("verdict") != v["verdict"]:
            delta = f"{before.get('verdict')}→{v['verdict']}"
        elif before.get("perf", "no-benchmark") != perf:
            delta = f"perf:{before.get('perf', 'no-benchmark')}→{perf}"
        else:
            delta = "unchanged"
        rows.append({**feat, "feature_family": family, "overlap_component": comp,
                     "verdict": v["verdict"], "reason": v["reason"], "regressed_checks": v["regressed_checks"],
                     "untestable_checks": v.get("untestable_checks", []),
                     "perf": perf, "delta": delta,
                     "cluster_key": f"{feat['class']}|{family}|c{comp if comp is not None else 'x'}|{v['verdict']}x{perf}"})
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    clusters: dict[str, list[str]] = {}
    for r in rows:
        clusters.setdefault(r["cluster_key"], []).append(r["branch"])
    perf_none = sum(1 for r in rows if r["perf"] == "no-benchmark")
    return {
        "schema": SCHEMA, "suite_version": SUITE_VERSION,
        "generated_at": now or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "registry_generated_at": registry.get("generated_at"),
        "feature_branches": len(rows), "verdict_counts": counts,
        "no_benchmark_share": round(perf_none / len(rows), 4) if rows else None,
        "clusters": [{"key": k, "branches": sorted(v)} for k, v in sorted(clusters.items())],
        "rows": rows,
        "policy": {"read_only": True, "untestable_counted_separately": True, "never_auto_merge": True},
    }


def _load(path: str | None) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8")) if path else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registry", required=True)
    ap.add_argument("--checks", required=True, help="{branch: {tip_sha, checks: {name: conclusion}}}")
    ap.add_argument("--baseline", required=True, help="{check name: conclusion} at master baseline")
    ap.add_argument("--prior")
    ap.add_argument("--files", help="{branch: [changed paths]}")
    ap.add_argument("--bench", help="{branch: {metric: {baseline, tip, higher_is_better}}}")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    result = build_map(_load(a.registry), _load(a.checks) or {}, _load(a.baseline) or {},
                       _load(a.prior), _load(a.files), _load(a.bench))
    Path(a.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"::notice title=brr-companion::feature_branches={result['feature_branches']} "
          f"verdicts={json.dumps(result['verdict_counts'], sort_keys=True)} clusters={len(result['clusters'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
