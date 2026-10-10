"""CodeRabbit file budget is advisory review capacity, not a promote ban."""
from __future__ import annotations

from ml.pipelines.recon08.rules import CODERABBIT_FILE_BUDGET


def budget_report(changed_files: int) -> dict[str, object]:
    return {
        "advisory_file_budget": CODERABBIT_FILE_BUDGET,
        "changed_files": changed_files,
        "within_advisory_budget": changed_files <= CODERABBIT_FILE_BUDGET,
        "is_promote_gate": False,
        "note": "Dual-gate on this SHA promotes. File count does not.",
    }
