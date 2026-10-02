#!/usr/bin/env python3
"""Emit privacy-preserving task-boundary identity for ATES.

The output contains hashes and execution metadata only. Raw task text never
enters the artifact, so the artifact can be consumed by a workflow_run observer
without exposing prompts, comments, or issue bodies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping


def digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    task_text = str(raw.get("task_text") or "")
    task_contract = {
        "agent_id": str(raw.get("agent_id") or ""),
        "task_kind": str(raw.get("task_kind") or ""),
        "target_kind": str(raw.get("target_kind") or ""),
        "target_number": str(raw.get("target_number") or ""),
        "repository": str(raw.get("repository") or ""),
        "base_sha": str(raw.get("base_sha") or ""),
        "task_text_sha256": hashlib.sha256(task_text.encode("utf-8")).hexdigest()
        if task_text else None,
    }
    environment = {
        "runner_os": str(raw.get("runner_os") or platform.system()),
        "runner_image": str(raw.get("runner_image") or ""),
        "workflow": str(raw.get("workflow") or ""),
        "provider": str(raw.get("provider") or ""),
        "model": str(raw.get("model") or ""),
    }
    record: dict[str, Any] = {
        "schema_version": "ates.task-boundary.v1",
        "agent_id": task_contract["agent_id"],
        "task_kind": task_contract["task_kind"],
        "target_kind": task_contract["target_kind"],
        "target_number": task_contract["target_number"],
        "task_fingerprint": digest(task_contract),
        "task_contract_hash": digest({
            "task_kind": task_contract["task_kind"],
            "repository": task_contract["repository"],
            "base_sha": task_contract["base_sha"],
        }),
        "environment_fingerprint": digest(environment),
        "provenance": {
            "repository": task_contract["repository"],
            "base_sha": task_contract["base_sha"],
        },
    }
    cohort_id = str(raw.get("cohort_id") or "").strip()
    if cohort_id:
        record["cohort_id"] = cohort_id
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    record = build_record(raw)
    Path(args.output).write_text(
        json.dumps(record, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
