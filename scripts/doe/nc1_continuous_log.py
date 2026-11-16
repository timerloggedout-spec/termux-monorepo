#!/usr/bin/env python3
"""nc-1 continuous population/diagnostic logger (owner order 2026-11-01;
cadence amendment same day).

Modes:
  run      — aggregate the Tier-1 layer-outputs population, append one
             population-log line + per-stratum density-stats lines.
             Each line carries cumulative per-stratum n (one-time
             backfill baseline + current population snapshot; snapshots
             are never summed across runs) and significance flags
             (n>=30 per the family honesty rule; below that the stats
             are NOT_ESTABLISHED and the line says so).
  backfill — one-time historical baseline from the telemetry lane's
             density-stats surface (ops/telemetry/density-stats.json,
             628 artifacts with per-artifact density + stratum).
             Idempotent on the source evidence_hash.

DIAGNOSTIC ONLY. Not a scored run: no verdicts, no floor checks, no
tau movement (tau/floors frozen; scored runs live in doe-nc1-eval.yml,
gated on the Linguist operator-set re-review). Fail-soft: internal
failure appends a DEFER line, exit 0.
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
SIG_N = 30  # family honesty rule: n>=30 (+ minority>=10, p<.05 downstream)


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


def _read_pop_log(logs_dir: Path) -> list[dict]:
    p = logs_dir / "population-log.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _append(logs_dir: Path, name: str, obj: dict) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    with open(logs_dir / name, "a") as fh:
        fh.write(json.dumps(obj, sort_keys=True) + "\n")


def backfill_baseline(lines: list[dict]) -> dict:
    base: dict[str, int] = {}
    for l in lines:
        if l.get("kind") == "backfill" and l.get("status") == "ok":
            for s, st in (l.get("per_stratum") or {}).items():
                base[s] = base.get(s, 0) + int(st.get("n") or 0)
    return base


def run(population_dir: Path, logs_dir: Path, observed_at: str) -> dict:
    files = sorted(glob.glob(str(population_dir / "shakedown-*.jsonl")))
    rows: list[dict] = []
    for f in files:
        for line in Path(f).read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    per = aggregate(rows)
    prior = _read_pop_log(logs_dir)
    base = backfill_baseline(prior)
    cumulative = {s: base.get(s, 0) + (per.get(s, {}) or {}).get("n", 0)
                  for s in STRATA}
    ids = sorted(str(r.get("unit_id")) for r in rows)
    prev_ids: set[str] = set()
    for l in reversed(prior):
        if l.get("kind") == "population-diagnostic" and l.get("status") == "ok":
            prev_ids = set(l.get("population_unit_ids") or [])
            break
    line = {
        "observed_at": observed_at,
        "kind": "population-diagnostic",
        "status": "ok",
        "instrument": "tier1-layer-outputs/v1 + nc1_continuous_log aggregate",
        "population_files": [Path(f).name for f in files],
        "population_hash": population_hash(rows),
        "population_units": len(rows),
        "population_unit_ids": ids,
        "window_new_units": len([i for i in ids if i not in prev_ids]) if prev_ids else None,
        "per_stratum": per,
        "cumulative_per_stratum_n": cumulative,
        "significance": {s: ("n>=30" if cumulative.get(s, 0) >= SIG_N
                             else "NOT_ESTABLISHED (n<30)")
                         for s in STRATA},
        "note": "diagnostic only; not a scored run; tau/floors frozen",
    }
    _append(logs_dir, "population-log.jsonl", line)
    for stratum, stats in per.items():
        _append(logs_dir, "density-stats.jsonl", {
            "observed_at": observed_at, "stratum": stratum,
            "population_hash": line["population_hash"], **stats})
    return line


def backfill(density_stats_path: Path, logs_dir: Path, observed_at: str) -> dict:
    doc = json.loads(density_stats_path.read_text())
    src_hash = doc.get("evidence_hash") or hashlib.sha256(
        density_stats_path.read_bytes()).hexdigest()
    prior = _read_pop_log(logs_dir)
    if any(l.get("kind") == "backfill" and l.get("source_hash") == src_hash
           for l in prior):
        line = {"observed_at": observed_at, "kind": "backfill",
                "status": "skip-duplicate", "source_hash": src_hash}
        _append(logs_dir, "population-log.jsonl", line)
        return line
    arts = doc.get("artifacts") or []
    per: dict[str, dict] = {}
    for stratum in STRATA:
        srows = [a for a in arts if a.get("stratum") == stratum]
        if not srows:
            continue
        dens = [float(a["density"]) for a in srows if a.get("density") is not None]
        per[stratum] = {
            "n": len(srows),
            "density_mean": round(statistics.fmean(dens), 4) if dens else None,
            "density_median": round(statistics.median(dens), 4) if dens else None,
            "outcomes": dict(Counter(a.get("outcome_kind") for a in srows)),
        }
    line = {"observed_at": observed_at, "kind": "backfill", "status": "ok",
            "source": "ops/telemetry/density-stats.json (telemetry ingest surface)",
            "source_hash": src_hash, "generated_at": doc.get("generated_at"),
            "per_stratum": per,
            "note": "one-time historical baseline; diagnostic only"}
    _append(logs_dir, "population-log.jsonl", line)
    for stratum, stats in per.items():
        _append(logs_dir, "density-stats.jsonl", {
            "observed_at": observed_at, "stratum": stratum,
            "backfill": True, "source_hash": src_hash, **stats})
    return line


def defer(logs_dir: Path, observed_at: str, reason: str) -> dict:
    line = {"observed_at": observed_at, "kind": "population-diagnostic",
            "status": "DEFER", "reason": reason[:200]}
    _append(logs_dir, "population-log.jsonl", line)
    return line


def main(argv: list[str]) -> int:
    observed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if len(argv) >= 2 and argv[1] == "backfill" and len(argv) == 4:
        try:
            line = backfill(Path(argv[2]), Path(argv[3]), observed_at)
            print(f"backfill: {line['status']} "
                  f"strata={ {k: v.get('n') for k, v in (line.get('per_stratum') or {}).items()} }")
        except Exception as exc:  # fail-soft
            defer(Path(argv[3]), observed_at, f"backfill {type(exc).__name__}: {exc}")
            print(f"DEFER recorded (backfill): {exc}")
        return 0
    if len(argv) != 3:
        print("usage: nc1_continuous_log.py <population_dir> <logs_dir>\n"
              "       nc1_continuous_log.py backfill <density_stats.json> <logs_dir>")
        return 2
    population_dir, logs_dir = Path(argv[1]), Path(argv[2])
    try:
        line = run(population_dir, logs_dir, observed_at)
        print(f"logged: {line['population_units']} units, "
              f"hash {line['population_hash']}, cumulative {line['cumulative_per_stratum_n']}")
    except Exception as exc:  # fail-soft: DEFER record, exit 0
        line = defer(logs_dir, observed_at, f"{type(exc).__name__}: {exc}")
        print(f"DEFER recorded: {line['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
