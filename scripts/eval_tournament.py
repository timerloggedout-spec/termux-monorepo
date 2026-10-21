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
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: each JSONL row must be an object")
        missing = {"candidate_id", "question_id", "expected", "prediction"} - row.keys()
        if missing:
            raise ValueError(f"{path}:{line_no}: missing required keys: {sorted(missing)}")
        for key in ("candidate_id", "question_id"):
            if not isinstance(row[key], (str, int)) or not str(row[key]).strip():
                raise ValueError(f"{path}:{line_no}: {key} must be a non-empty string or integer")
        rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no receipt rows")
    return rows


def _valid_latency(row: dict[str, Any]) -> float | None:
    value = row.get("latency_ms")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) and value >= 0 else None


def score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("no receipt rows")
    by_candidate: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} must be an object")
        missing = {"candidate_id", "question_id", "expected", "prediction"} - row.keys()
        if missing:
            raise ValueError(f"row {index}: missing required keys: {sorted(missing)}")
        candidate = str(row["candidate_id"]).strip()
        question = str(row["question_id"]).strip()
        if not candidate or not question:
            raise ValueError(f"row {index}: candidate_id and question_id must be non-empty")
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
            "Missing question IDs are not silently imputed; pairwise comparison uses intersection only.",
            "Pairwise ties and non-comparable infrastructure failures are reported separately."
        ]
    }

    for candidate in candidates:
        items = list(by_candidate[candidate].values())
        comparable = [r for r in items if r.get("status", "ok") == "ok" and r.get("expected") is not None]
        correct = sum(r.get("prediction") == r.get("expected") for r in comparable)
        latency = [v for r in items if (v := _valid_latency(r)) is not None]
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
            "non_ok_status_count": sum(r.get("status", "ok") != "ok" for r in items),
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
            left_wins = right_wins = ties_both_correct = ties_both_incorrect = non_comparable = 0
            for qid in shared:
                a = by_candidate[left][qid]
                b = by_candidate[right][qid]
                if (
                    a.get("expected") is None or b.get("expected") is None
                    or a.get("status", "ok") != "ok" or b.get("status", "ok") != "ok"
                ):
                    non_comparable += 1
                    continue
                a_ok = a["prediction"] == a["expected"]
                b_ok = b["prediction"] == b["expected"]
                if a_ok and b_ok:
                    ties_both_correct += 1
                elif not a_ok and not b_ok:
                    ties_both_incorrect += 1
                elif a_ok:
                    left_wins += 1
                else:
                    right_wins += 1
            decisive = left_wins + right_wins
            report["pairwise"].append({
                "left": left, "right": right,
                "shared_questions": len(shared),
                "comparable_questions": len(shared) - non_comparable,
                "non_comparable_questions": non_comparable,
                "decisive_questions": decisive,
                "left_wins": left_wins, "right_wins": right_wins,
                "ties_both_correct": ties_both_correct,
                "ties_both_incorrect": ties_both_incorrect,
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
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
