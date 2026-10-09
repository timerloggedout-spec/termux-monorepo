#!/usr/bin/env python3
"""Contract tests for cancelled-only Actions incident suppression."""

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).with_name("classify_workflow_jobs.py")
    spec = importlib.util.spec_from_file_location("classify_workflow_jobs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cancelled_only_is_not_actionable():
    module = _load()
    result = module.classify(
        [
            {"name": "audit", "conclusion": "cancelled"},
            {"name": "notify", "conclusion": "skipped"},
        ]
    )
    assert result["actionable"] is False
    assert result["actionable_jobs"] == []


def test_failure_job_is_actionable():
    module = _load()
    result = module.classify(
        [
            {"name": "ledger", "conclusion": "failure"},
            {"name": "audit", "conclusion": "cancelled"},
        ]
    )
    assert result["actionable"] is True
    assert result["actionable_jobs"] == [{"name": "ledger", "conclusion": "failure"}]


def test_timed_out_job_is_actionable():
    module = _load()
    result = module.classify([{"name": "ledger", "conclusion": "timed_out"}])
    assert result["actionable"] is True


if __name__ == "__main__":
    test_cancelled_only_is_not_actionable()
    test_failure_job_is_actionable()
    test_timed_out_job_is_actionable()
    print("ok")
