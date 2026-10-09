"""Next operator actions. Does not merge, comment, or restamp LANE-MATRIX.md."""
from __future__ import annotations

from typing import Any

from ml.pipelines.recon07.delta import disagreements, summary
from ml.pipelines.recon07.registry import evaluate_rules, load_observations
from ml.pipelines.recon07.stamp import stamp_report


def _counts(kind: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for obs in load_observations():
        if obs.kind != kind:
            continue
        counts[obs.lane] = counts.get(obs.lane, 0) + 1
    return counts


def next_actions() -> list[dict[str, Any]]:
    return [
        {
            "p": 0,
            "action": "Keep product SHA 8d36f149 until dual-gate SUCCESS on a new product commit.",
            "lane": "CANDIDATE",
        },
        {
            "p": 0,
            "action": "Treat observer tip 9dc1e437 as help-wanted NON-PROMOTE.",
            "lane": "SUPERSEDE",
        },
        {
            "p": 0,
            "action": "Edit Issue #175 body (stamp 8424a50c is stale). Do not pulse-comment.",
            "lane": "NEED_EVIDENCE",
        },
        {
            "p": 0,
            "action": "Leave wholesale ML #432 #549 #601 #682 #746 #787 #817 on EXTRACT.",
            "lane": "EXTRACT",
        },
        {
            "p": 0,
            "action": "Do not overwrite minesweeper peers (#65 #140 #630 #680 #1185 #1186 and Jules family).",
            "lane": "EXTRACT",
        },
        {
            "p": 1,
            "action": "Do not retarget #48 or #788 off master-staging.",
            "lane": "NEED_EVIDENCE",
        },
        {
            "p": 1,
            "action": "Rebase #806 and #809 as small slices; promote only with dual-gate on that SHA.",
            "lane": "NEED_EVIDENCE",
        },
        {
            "p": 1,
            "action": "Actions incidents #1023 #1024 #1025 #1026 stay evidence gaps, not promote gates.",
            "lane": "NEED_EVIDENCE",
        },
        {
            "p": 2,
            "action": "CodeRabbit ~100-file budget is advisory. Vercel/Qodo/Devin/Copilot are non-gate.",
            "lane": "SUPERSEDE",
        },
    ]


def report() -> dict[str, Any]:
    findings = evaluate_rules(stamp_report())
    failed = [row.rule_id for row in findings if not row.ok]
    return {
        "stamp": stamp_report(),
        "catalog_prs": _counts("pr"),
        "catalog_issues": _counts("issue"),
        "delta": summary(disagreements()),
        "rules_failed": failed,
        "rules_ok": len(findings) - len(failed),
        "next": next_actions(),
        "writes": False,
    }
