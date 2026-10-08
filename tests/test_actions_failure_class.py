import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "actions_failure_class",
    ROOT / "scripts/ci/actions_failure_class.py",
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_ghost_queued_disabled_is_not_a_filename_failure():
    run = {
        "id": 37655538554,
        "name": "Merge Promotion Queue",
        "path": ".github/workflows/merge-promotion-queue.yml",
        "status": "queued",
        "conclusion": None,
        "workflow_state": "disabled_manually",
    }
    assert mod.classify_run(run) == "ghost_queued_disabled"
    assert mod.master_gate_blocked([run]) is False


def test_filename_named_failure_blocks_master_gate():
    run = {
        "id": 1,
        "name": ".github/workflows/sweep-accountability.yml",
        "path": ".github/workflows/sweep-accountability.yml",
        "status": "completed",
        "conclusion": "failure",
        "workflow_state": "active",
    }
    assert mod.classify_run(run) == "filename_failure"
    assert mod.master_gate_blocked([run]) is True


def test_named_job_failure_is_distinct_from_filename_class():
    run = {
        "id": 2,
        "name": "Action Effectiveness Ledger",
        "path": ".github/workflows/action-effectiveness-ledger.yml",
        "status": "completed",
        "conclusion": "failure",
        "workflow_state": "active",
    }
    assert mod.classify_run(run) == "job_failure"
    assert mod.master_gate_blocked([run]) is False


def test_summary_keeps_ghost_id_and_does_not_block():
    runs = [
        {
            "id": 37655538554,
            "name": "Merge Promotion Queue",
            "status": "queued",
            "conclusion": None,
            "workflow_state": "disabled_manually",
        },
        {
            "id": 37726528537,
            "name": "Agent Runtime Stall Watch",
            "status": "completed",
            "conclusion": "success",
            "workflow_state": "active",
        },
    ]
    summary = mod.summarize(runs)
    assert summary["master_gate_blocked"] is False
    assert summary["ghost_run_ids"] == [37655538554]
    assert summary["counts"]["success"] == 1
    assert summary["counts"]["ghost_queued_disabled"] == 1
