#!/usr/bin/env python3
"""Bounded parallel evaluator for the versioned classifier question bank.

The default deterministic baseline is a wiring check, not a model-quality
benchmark. Candidate-by-question jobs run concurrently under global and
per-candidate limits; output order remains stable regardless of completion
order. Mock, unavailable, unsupported, and live inference are distinct states.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = ROOT / "tests/fixtures/classifier-question-bank.json"
CANDIDATES = ("deterministic-baseline", "laya-mock", "laya-live", "jev")
MODEL_REFS = {
    "deterministic-baseline": ("deterministic-baseline@1", "python-stdlib@1", "builtin-rules@1"),
    "laya-mock": ("laya-contract-mock", "python-stdlib@1", "laya-decision-stub@1"),
    "laya-live": ("laya-live-configured", "local-runtime@unknown", "laya-router-adapter@1"),
    "jev": (os.getenv("TYPESAFE_MODEL", "jev-latest"), "hosted-api@typesafe", "typesafe-systemone-adapter@1"),
}


def baseline_predict(question: dict[str, Any]) -> tuple[Any, str, bool]:
    task = question["task"]
    text = question["input"].lower()
    if task == "text_classification":
        if any(token in text for token in ("invoice", "charged twice", "refund", "cobraron", "reembolso")):
            return "billing", "deterministic_keyword_rule", False
        if any(token in text for token in ("lost access", "my account", "changing my phone", "account access")):
            return "account_access", "deterministic_keyword_rule", False
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
            token = "#1450" if entity == "ISSUE_ID" else (
                "https://github.com/urchade/GLiNER" if entity == "URL" else ""
            )
            start = question["input"].find(token) if token else -1
            if start >= 0:
                spans.append({"text": token, "label": entity, "start": start, "end": start + len(token)})
        return spans, "deterministic_fixture_extractor", False
    return None, "unsupported_task", True


def _decision_payload(question: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Map bank items to the shared Choice shape where semantics are compatible."""
    task = question.get("task")
    if task == "text_classification":
        labels = question.get("label_ontology") or []
        criteria = {label: label.replace("_", " ") for label in labels}
        prompt = "Choose the single best label. If evidence is insufficient, choose ABSTAIN."
        if "ABSTAIN" not in criteria:
            criteria["ABSTAIN"] = "insufficient evidence; do not guess"
    elif task == "typed_choice":
        source = question.get("question") or {}
        options = source.get("options") or []
        criteria = {option: option.replace("_", " ") for option in options}
        prompt = source.get("prompt") or "Choose the best available option."
    else:
        return None
    state = {"subject": question.get("question_id", ""), "body": question["input"], "language": question.get("language", "unknown")}
    query = {"answer": {"type": "choice", "instructions": prompt, "criteria": criteria}}
    return state, query


def _predict_candidate(candidate: str, question: dict[str, Any], live: bool) -> tuple[str, Any, str, bool, str | None]:
    """Return status, prediction, adapter ref, abstained, error class."""
    if candidate == "deterministic-baseline":
        prediction, method, abstained = baseline_predict(question)
        return "OK", prediction, method, abstained, None

    payload = _decision_payload(question)
    if payload is None:
        return "NOT_APPLICABLE", None, "task-not-supported-by-choice-adapter", False, "UNSUPPORTED_TASK"

    state, questions = payload
    if candidate == "laya-mock":
        try:
            from scripts.laya_decision_stub import mock_predict
            raw = mock_predict(state, questions)
            answer = raw.get("answers", {}).get("answer", {})
            prediction = answer.get("choice", "ABSTAIN")
            return "MOCK", prediction, "laya-decision-stub@1", prediction == "ABSTAIN", None
        except Exception as exc:
            return "ERROR", None, "laya-decision-stub@1", False, type(exc).__name__

    if not live:
        return "UNAVAILABLE", None, candidate + "-live-disabled", False, "ENGINE_UNAVAILABLE"

    if candidate == "laya-live":
        try:
            from scripts.laya_decision_stub import live_predict
            raw = live_predict(state, questions)
            answer = raw.get("answers", {}).get("answer", {})
            prediction = answer.get("choice", "ABSTAIN")
            return "OK", prediction, "laya-router-live@1", prediction == "ABSTAIN", None
        except (ImportError, RuntimeError) as exc:
            return "UNAVAILABLE", None, "laya-router-live@1", False, "ENGINE_UNAVAILABLE"
        except Exception as exc:
            return "ERROR", None, "laya-router-live@1", False, type(exc).__name__

    if candidate == "jev":
        try:
            from scripts.system_one_adapters import DecisionRequest, TypeSafeJevAdapter
            request = DecisionRequest(
                state=state,
                questions=questions,
                experiment_id="classifier-eval",
                lane_id="parallel",
                category="routing",
            )
            result = TypeSafeJevAdapter().evaluate(request)
            if result.status != "OK":
                return result.status, None, "typesafe-systemone-adapter@1", False, result.metadata.get("failure_class")
            answer = result.answers.get("answer", {})
            prediction = answer.get("choice", "ABSTAIN") if isinstance(answer, dict) else "ABSTAIN"
            return "OK", prediction, "typesafe-systemone-adapter@1", prediction == "ABSTAIN", None
        except Exception as exc:
            return "ERROR", None, "typesafe-systemone-adapter@1", False, type(exc).__name__

    return "ERROR", None, "unknown-adapter", False, "UNKNOWN_CANDIDATE"


def _is_correct(question: dict[str, Any], prediction: Any) -> bool | None:
    if question.get("task") == "span_extraction":
        return prediction == question.get("expected_spans")
    expected = question.get("expected")
    if expected is None:
        return None
    acceptable = question.get("acceptable_outputs")
    if not isinstance(acceptable, list) or not acceptable:
        acceptable = [expected]
    return any(prediction == item for item in acceptable)


def evaluate_one(
    question: dict[str, Any],
    bank_version: str,
    run_id: str,
    source_commit: str,
    candidate: str = "deterministic-baseline",
    live: bool = False,
    candidate_semaphore: threading.Semaphore | None = None,
) -> dict[str, Any]:
    queued_at = time.perf_counter()
    if candidate_semaphore is not None:
        candidate_semaphore.acquire()
    started = time.perf_counter()
    queue_ms = round((started - queued_at) * 1000, 3)
    try:
        status, prediction, adapter_ref, abstained, error_class = _predict_candidate(candidate, question, live)
        correct = _is_correct(question, prediction) if status == "OK" else None
    except Exception as exc:
        status, prediction, adapter_ref, abstained = "ERROR", None, "evaluation-harness@1", False
        correct, error_class = None, type(exc).__name__
    finally:
        if candidate_semaphore is not None:
            candidate_semaphore.release()

    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    model_ref, runtime_ref, default_adapter_ref = MODEL_REFS[candidate]
    input_text = question["input"]
    return {
        "schema_version": "classifier-eval.v1",
        "run_id": run_id,
        "bank_version": bank_version,
        "question_id": question["question_id"],
        "candidate_id": candidate,
        "model_ref": model_ref,
        "runtime_ref": runtime_ref,
        "adapter_ref": adapter_ref or default_adapter_ref,
        "task": question["task"],
        "language": question["language"],
        "split": question["split"],
        "status": status,
        "prediction": prediction,
        "scores": None,
        "score_semantics": "none",
        "abstained": abstained,
        "expected": question.get("expected", question.get("expected_spans")),
        "acceptable_outputs": question.get("acceptable_outputs"),
        "correct": correct,
        "queue_ms": queue_ms,
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
    parser.add_argument("--workers", type=int, default=8, help="global concurrent job limit (1-64)")
    parser.add_argument("--per-candidate-workers", type=int, default=2, help="concurrency limit per candidate (1-16)")
    parser.add_argument("--candidates", nargs="+", choices=CANDIDATES, default=["deterministic-baseline"])
    parser.add_argument("--live", action="store_true", help="allow configured live Laya/Jev requests")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--source-commit", default="")
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 64:
        parser.error("--workers must be between 1 and 64")
    if args.per_candidate_workers < 1 or args.per_candidate_workers > 16:
        parser.error("--per-candidate-workers must be between 1 and 16")
    bank = json.loads(args.bank.read_text(encoding="utf-8"))
    questions = bank.get("questions")
    if not isinstance(questions, list) or not questions:
        parser.error("question bank must contain a non-empty questions array")
    ids = [q.get("question_id") for q in questions]
    if any(not isinstance(qid, str) or not qid for qid in ids) or len(set(ids)) != len(ids):
        parser.error("question_id values must be non-empty and unique")
    run_id = args.run_id or "classifier-eval-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidates = list(dict.fromkeys(args.candidates))
    semaphores = {candidate: threading.Semaphore(args.per_candidate_workers) for candidate in candidates}
    jobs = [(qi, ci, q, candidate) for qi, q in enumerate(questions) for ci, candidate in enumerate(candidates)]
    receipts: list[dict[str, Any] | None] = [None] * len(jobs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                evaluate_one, q, bank["schema_version"], run_id, args.source_commit,
                candidate, args.live, semaphores[candidate],
            ): index
            for index, (_, _, q, candidate) in enumerate(jobs)
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
