"""Classify Actions runs so ghost queued disabled workflows are not filename failures.

Evidence binding (2026-10-08): master tip 000c9391ebdb4decb6669cfc8bd4709f11d55e7d
had no conclusion=failure in the latest completed sample. Run 37655538554 remains
queued on disabled_manually workflow 354842048; cancel returns HTTP 409
("not been queued yet"). That run must not open another workflow id and must not
be promoted as a master gate failure.
"""

from __future__ import annotations

GHOST_CANCEL_STATUSES = {409}


def classify_run(run: dict) -> str:
    """Return a stable class label for one Actions run record.

    Labels:
      - filename_failure: completed failure whose name is the workflow path
      - job_failure: completed failure with a human workflow name
      - ghost_queued_disabled: queued/requested on a disabled workflow
      - success / skipped / cancelled / in_progress / queued / other
    """
    status = str(run.get("status") or "")
    conclusion = run.get("conclusion")
    name = str(run.get("name") or "")
    path = str(run.get("path") or "")
    workflow_state = str(run.get("workflow_state") or "")
    if status in {"queued", "requested", "waiting"} and workflow_state in {
        "disabled_manually",
        "disabled_inactivity",
    }:
        return "ghost_queued_disabled"
    if conclusion == "failure":
        if name.startswith(".github/workflows/") or name == path:
            return "filename_failure"
        return "job_failure"
    if conclusion in {"success", "skipped", "cancelled"}:
        return str(conclusion)
    if status:
        return status
    return "other"


def master_gate_blocked(runs: list[dict]) -> bool:
    """True only when a completed filename-named failure is present.

    Ghost queued runs on disabled workflows do not block promotion.
    """
    return any(classify_run(run) == "filename_failure" for run in runs)


def summarize(runs: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for run in runs:
        label = classify_run(run)
        counts[label] = counts.get(label, 0) + 1
    return {
        "schema": "actions-failure-class/v1",
        "counts": counts,
        "master_gate_blocked": master_gate_blocked(runs),
        "ghost_run_ids": [
            run.get("id")
            for run in runs
            if classify_run(run) == "ghost_queued_disabled"
        ],
    }
