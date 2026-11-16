"""Reconcile locally reconstructed stats against UI CSV export rows."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


def reconcile_main(args: Any) -> int:
    csv_path: Path = args.csv
    derived_path: Path = args.derived
    tol = float(args.tolerance_pp)

    derived = json.loads(derived_path.read_text(encoding="utf-8"))
    recon_rate = float(derived.get("failure_rate_pct") or 0.0)

    rows: list[dict[str, str]] = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # If derived is window-wide, compare only when a single workflow filter was used;
    # otherwise report reconstructed rate and list UI top failures for operator review.
    report: dict[str, Any] = {
        "derived_failure_rate_pct": recon_rate,
        "derived_run_count": derived.get("run_count"),
        "ui_csv": str(csv_path),
        "tolerance_pp": tol,
        "label": "locally_reconstructed",
        "ui_top_failures": [],
        "status": "review",
    }

    for row in rows[:15]:
        try:
            rate = float(str(row.get("Has job failures") or row.get("failure_rate") or "0").replace("%", ""))
        except ValueError:
            rate = 0.0
        report["ui_top_failures"].append(
            {
                "workflow": row.get("Workflow") or row.get("workflow"),
                "failure_pct": rate,
                "runs": row.get("Workflow runs") or row.get("runs"),
            }
        )

    # Single-workflow reconcile if derived metadata names one workflow
    wf = derived.get("workflow") or derived.get("workflow_filter")
    if wf:
        match = next(
            (
                r
                for r in rows
                if wf in str(r.get("Workflow") or "")
            ),
            None,
        )
        if match:
            try:
                ui_rate = float(
                    str(match.get("Has job failures") or "0").replace("%", "")
                )
            except ValueError:
                ui_rate = 0.0
            delta = abs(ui_rate - recon_rate)
            report["ui_workflow"] = match.get("Workflow")
            report["ui_failure_pct"] = ui_rate
            report["delta_pp"] = delta
            report["status"] = "pass" if delta <= tol else "fail"

    print(json.dumps(report, indent=2))
    return 0 if report["status"] != "fail" else 1
