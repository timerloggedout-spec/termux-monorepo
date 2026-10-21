#!/usr/bin/env python3
"""Bounded, deterministic smoke runner for the versioned classifier question bank.

This baseline is a contract/wiring check, not a model-quality benchmark. Live
model adapters should implement the same receipt contract and be evaluated on
the same question IDs.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = ROOT / "tests/fixtures/classifier-question-bank.json"


def baseline_predict(question: dict[str, Any]) -> tuple[Any, str, bool]:
    task = question["task"]
    text = question["input"].lower()
    if task == "text_classification":
        if any(token in text for token in ("invoice", "charged twice", "refund", "cobraron", "reembolso")):
            return "billing", "deterministic_keyword_rule", False
        if any(token in text for token in ("ignore all policy", "print the stored api key")):
            return "prompt_injection_attempt", "deterministic_keyword_rule", False
        if text == "it stopped working yesterday.":
            return "ABSTAIN", "insufficient_context_rule", True
        return "ABSTAIN", "no_matching_rule", True
    if task == "typed_choice":
        if "exact internal state" in text or "without telemetry" in text:
            return "unknown", "insufficient_evidence_rule", True
        if "conflicting evidence" in text:
            return "gather_evidence", "conflicting_evidence_rule", False
        return "ABSTAIN", "no_matching_rule", True
    if task == "multilabel_classification":
        labels = []
        if "network" in text or "network change" in text:
            labels.append("network")
        if "503" in text or "provider" in text:
            labels.append("provider")
        return labels, "deterministic_keyword_rule", not bool(labels)
    if task == "span_extraction":
        spans = []
        for entity in question.get("entity_types", []):
            if entity == "ISSUE_ID":
                token = "#1450"
                start = question["input"].find(token)
                if start >= 0:
                    spans.append({"text": token, "label": entity, "start": start, "end": start + len(token)})
            elif entity == "URL":
                token = "https://github.com/urchade/GLiNER"
                start = question["input"].find(token)
                if start >= 0:
                    spans.append({"text": token, "label": entity, "start": start, "end": start + len(token)})
        return spans, "deterministic_fixture_extractor", False
    return None, "unsupported_task", True


def evaluate_one(question: dict[str, Any], bank_version: str, run_id: str, source_commit: str) -> dict[str, Any]:
    started = time.perf_counter()
    input_text = question["input"]
    try:
        prediction, method, abstained = baseline_predict(question)
        if question["task"] == "span_extraction":
            expected = question["expected_spans"]
            correct = prediction == expected
        else:
            expected = question.get("expected")
            acceptable = question.get("acceptable_outputs", [expected])
            correct = prediction in acceptable if isinstance(acceptable, list) and (
                not acceptable or not isinstance(acceptable[0], list)
            ) else prediction == expected
        status = "OK"
        error_class = None
    except Exception as exc:  # one bad item must not terminate the cohort
        prediction, method, abstained, expected = None, "baseline_error", False, question.get("expected")
        correct, status, error_class = None, "ERROR", type(exc).__name__
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "schema_version": "classifier-eval.v1",
        "run_id": run_id,
        "bank_version": bank_version,
        "question_id": question["question_id"],
        "candidate_id": "deterministic-baseline",
        "model_ref": "deterministic-baseline@1",
        "runtime_ref": "python-stdlib",
        "adapter_ref": method,
        "task": question["task"],
        "language": question["language"],
        "split": question["split"],
        "status": status,
        "prediction": prediction,
        "scores": None,
        "score_semantics": "none",
        "abstained": abstained,
        "expected": expected,
        "correct": correct,
        "queue_ms": None,
        "latency_ms": elapsed_ms,
        "attempt": 1,
        "input_sha256": "sha256:" + hashlib.sha256(input_text.encode()).hexdigest(),
        "source_commit": source_commit or None,
        "error_class": error_class,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--output", type=Path, help="JSONL output path; stdout if omitted")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--source-commit", default="")
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 64:
        parser.error("--workers must be between 1 and 64")
    bank = json.loads(args.bank.read_text(encoding="utf-8"))
    questions = bank.get("questions")
    if not isinstance(questions, list) or not questions:
        parser.error("question bank must contain a non-empty questions array")
    ids = [q.get("question_id") for q in questions]
    if any(not isinstance(qid, str) or not qid for qid in ids) or len(set(ids)) != len(ids):
        parser.error("question_id values must be non-empty and unique")
    run_id = args.run_id or "classifier-eval-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    indexed = list(enumerate(questions))
    receipts: list[dict[str, Any] | None] = [None] * len(indexed)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(evaluate_one, q, bank["schema_version"], run_id, args.source_commit): index
            for index, q in indexed
        }
        for future in concurrent.futures.as_completed(futures):
            receipts[futures[future]] = future.result()
    lines = [json.dumps(row, sort_keys=True, ensure_ascii=False) for row in receipts if row is not None]
    payload = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
