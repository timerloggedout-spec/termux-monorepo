"""Pure reduce/reconcile smoke tests (no network)."""
from __future__ import annotations

import json
from pathlib import Path

from ops.github_telemetry.reduce import reduce_main
from ops.github_telemetry.reconcile import reconcile_main


def test_reduce_from_jobs_files(tmp_path: Path):
    jobs = {
        "jobs": [
            {
                "id": 1,
                "run_id": 100,
                "name": "x",
                "conclusion": "failure",
                "started_at": "2020-01-20T17:00:00Z",
                "completed_at": "2020-01-20T17:03:00Z",
            }
        ]
    }
    f = tmp_path / "jobs-100.json"
    f.write_text(json.dumps({"data": jobs}), encoding="utf-8")
    out_dir = tmp_path / "out"

    class Args:
        jobs_file = [f]
        jobs_glob = ""
        window_label = "test"
        out = out_dir

    assert reduce_main(Args()) == 0
    reports = list(out_dir.glob("actions-performance-reconstructed-*.json"))
    assert len(reports) == 1
    body = json.loads(reports[0].read_text(encoding="utf-8"))
    assert body["failure_rate_pct"] == 100.0
    assert body["label"] == "locally_reconstructed"


def test_reconcile_review_mode(tmp_path: Path):
    csv_path = tmp_path / "ui.csv"
    csv_path.write_text(
        "Workflow,Has job failures,Avg run time,Workflow runs,Jobs\n"
        ".github/workflows/agentic-repository-operations-report.lock.yml,100.00,187958,6,5\n",
        encoding="utf-8",
    )
    derived_file = tmp_path / "derived.json"
    derived_file.write_text(
        json.dumps(
            {
                "failure_rate_pct": 100.0,
                "run_count": 6,
                "label": "locally_reconstructed",
            }
        ),
        encoding="utf-8",
    )

    class Args:
        csv = csv_path
        derived = derived_file
        tolerance_pp = 2.0

    assert reconcile_main(Args()) == 0
