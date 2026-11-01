#!/usr/bin/env python3
"""nc-1 continuous population/diagnostic logger (owner order 2026-11-01).

Runs the existing notation/density scorer stack's DIAGNOSTIC side over
the layer-outputs population and appends one record per run to the
in-repo continuous logs:

  records/logs/population-log.jsonl  (one line per run)
  records/logs/density-stats.jsonl   (one line per stratum per run)

This is diagnostic/population logging ONLY. It is not a scored run:
no verdict, no floor checks, no tau movement (tau/floors frozen;
scored runs live in doe-nc1-eval.yml and stay gated on the Linguist
operator-set re-review). Fail-soft: any internal failure appends a
DEFER line and exits 0 (prior-lane DEFER-record pattern), so a bad
window shows up in the log instead of vanishing.

Population rows are the Tier-1 layer-outputs units (density and
tokens precomputed by their pipeline; layer_verdict = their as-built
v1 rule). Aggregation here is pure stdlib over those rows.
"""
from __future__ import annotations

import glob
import hashlib
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

STRATA = ("chat", "github", "docs", "records")


def aggregate(rows: list[dict]) -> dict:
    per: dict[str, dict] = {}
    for stratum in STRATA:
        srows = [r for r in rows if r.get("stratum") == stratum]
        if not srows:
            continue
        dens = [float(r["density"]) for r in srows if r.get("density") is not None]
        per[stratum] = {
            "n": len(srows),
            "density_mean": round(statistics.fmean(dens), 4) if dens else None,
            "density_median": round(statistics.median(dens), 4) if dens else None,
            "tokens_total": sum(int(r.get("tokens_scanned") or 0) for r in srows),
            "by_layer": dict(Counter(r.get("layer") for r in srows)),
            "layer_verdicts": {
                "drift": sum(1 for r in srows
                             if (r.get("layer_verdict") or {}).get("drift")),
                "borderline": sum(1 for r in srows
                                  if (r.get("layer_verdict") or {}).get("borderline")),
                "score_mean": round(statistics.fmean(
                    [float(r["layer_verdict"]["score"]) for r in srows
                     if (r.get("layer_verdict") or {}).get("score") is not None]), 4)
                if any((r.get("layer_verdict") or {}).get("score") is not None
                       for r in srows) else None,
            },
            "class_hints": dict(Counter(r.get("class_hint") for r in srows
                                         if r.get("class_hint"))),
        }
    return per


def population_hash(rows: list[dict]) -> str:
    h = hashlib.sha256()
    for r in sorted(rows, key=lambda x: str(x.get("unit_id"))):
        h.update(json.dumps(r, sort_keys=True).encode())
        h.update(b"\n")
    return h.hexdigest()[:16]


def run(population_dir: Path, logs_dir: Path, observed_at: str) -> dict:
    files = sorted(glob.glob(str(population_dir / "shakedown-*.jsonl")))
    rows: list[dict] = []
    for f in files:
        for line in Path(f).read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    per = aggregate(rows)
    phash = population_hash(rows)
    logs_dir.mkdir(parents=True, exist_ok=True)
    pop_line = {
        "observed_at": observed_at,
        "kind": "population-diagnostic",
        "status": "ok",
        "instrument": "tier1-layer-outputs/v1 + nc1_continuous_log aggregate",
        "population_files": [Path(f).name for f in files],
        "population_hash": phash,
        "population_units": len(rows),
        "per_stratum": per,
        "note": "diagnostic only; not a scored run; tau/floors frozen",
    }
    with open(logs_dir / "population-log.jsonl", "a") as fh:
        fh.write(json.dumps(pop_line, sort_keys=True) + "\n")
    with open(logs_dir / "density-stats.jsonl", "a") as fh:
        for stratum, stats in per.items():
            fh.write(json.dumps({
                "observed_at": observed_at,
                "stratum": stratum,
                "population_hash": phash,
                **stats,
            }, sort_keys=True) + "\n")
    return pop_line


def defer(logs_dir: Path, observed_at: str, reason: str) -> dict:
    logs_dir.mkdir(parents=True, exist_ok=True)
    line = {"observed_at": observed_at, "kind": "population-diagnostic",
            "status": "DEFER", "reason": reason[:200]}
    with open(logs_dir / "population-log.jsonl", "a") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")
    return line


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: nc1_continuous_log.py <population_dir> <logs_dir>")
        return 2
    population_dir, logs_dir = Path(argv[1]), Path(argv[2])
    observed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        line = run(population_dir, logs_dir, observed_at)
        print(f"logged: {line['population_units']} units, "
              f"hash {line['population_hash']}, strata {sorted(line['per_stratum'])}")
    except Exception as exc:  # fail-soft: DEFER record, exit 0
        line = defer(logs_dir, observed_at, f"{type(exc).__name__}: {exc}")
        print(f"DEFER recorded: {line['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
