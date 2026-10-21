#!/usr/bin/env python3
"""Score candidate JSONL receipts and produce a deterministic pairwise tournament.

Input rows require: candidate_id, question_id, expected, prediction.
Optional fields: latency_ms, status, schema_valid, judge_id, judge_verdict.
This is an offline evaluator; it never calls models or treats peer judgments as ground truth.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        missing = {"candidate_id", "question_id", "expected", "prediction"} - row.keys()
        if missing:
            raise ValueError(f"{path}:{line_no}: missing required keys: {sorted(missing)}")
        rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no receipt rows")
    return rows


def score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_candidate: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        candidate = str(row["candidate_id"])
        question = str(row["question_id"])
        if question in by_candidate[candidate]:
            raise ValueError(f"duplicate question_id={question!r} for candidate={candidate!r}")
        by_candidate[candidate][question] = row

    candidates = sorted(by_candidate)
    report: dict[str, Any] = {
        "schema_version": "system-one-tournament.v1",
        "source_rows": len(rows),
        "candidates": {},
        "pairwise": [],
        "limitations": [
            "Exact-match accuracy is meaningful only when expected/prediction semantics are canonicalized.",
            "Peer/judge verdicts are not ground truth and are not used in accuracy.",
            "Latency is descriptive and must be measured under matched hardware/load conditions.",
            "Missing question IDs are not silently imputed; pairwise comparison uses intersection only."
        ]
    }

    for candidate in candidates:
        items = list(by_candidate[candidate].values())
        comparable = [r for r in items if r.get("status", "ok") == "ok" and r.get("expected") is not None]
        correct = sum(r.get("prediction") == r.get("expected") for r in comparable)
        latency = [float(r["latency_ms"]) for r in items if isinstance(r.get("latency_ms"), (int, float)) and r["latency_ms"] >= 0]
        abstentions = sum(
            str(r.get("prediction", "")).upper() in {"ABSTAIN", "UNKNOWN", "UNSURE"}
            for r in items
        )
        invalid_schema = sum(r.get("schema_valid") is False for r in items)
        report["candidates"][candidate] = {
            "receipt_count": len(items),
            "scored_count": len(comparable),
            "exact_match_accuracy": correct / len(comparable) if comparable else None,
            "correct": correct,
            "incorrect": len(comparable) - correct,
            "abstention_count": abstentions,
            "abstention_rate": abstentions / len(items),
            "schema_invalid_count": invalid_schema,
            "latency_ms": {
                "count": len(latency),
                "mean": statistics.fmean(latency) if latency else None,
                "p50": quantile(latency, 0.50),
                "p95": quantile(latency, 0.95),
                "max": max(latency) if latency else None
            }
        }

    for i, left in enumerate(candidates):
        for right in candidates[i + 1:]:
            shared = sorted(set(by_candidate[left]) & set(by_candidate[right]))
            judged = []
            ties = 0
            for qid in shared:
                a = by_candidate[left][qid]
                b = by_candidate[right][qid]
                if a.get("expected") is None or b.get("expected") is None:
                    continue
                a_ok = a.get("status", "ok") == "ok" and a["prediction"] == a["expected"]
                b_ok = b.get("status", "ok") == "ok" and b["prediction"] == b["expected"]
                if a_ok and b_ok:
                    ties += 1
                else:
                    judged.append({"question_id": qid, "left_correct": bool(a_ok), "right_correct": bool(b_ok)})
            left_wins = sum(x["left_correct"] and not x["right_correct"] for x in judged)
            right_wins = sum(x["right_correct"] and not x["left_correct"] for x in judged)
            decisive = left_wins + right_wins
            report["pairwise"].append({
                "left": left, "right": right,
                "shared_questions": len(shared),
                "decisive_questions": decisive,
                "left_wins": left_wins, "right_wins": right_wins,
                "ties_both_correct": ties,
                "left_win_rate_decisive": left_wins / decisive if decisive else None
            })
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSONL file containing normalized candidate receipts")
    parser.add_argument("--output", type=Path, help="write report JSON to this path; stdout otherwise")
    args = parser.parse_args(argv)
    try:
        report = score(load_rows(args.input))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
