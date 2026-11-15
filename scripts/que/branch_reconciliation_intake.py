"""BRR-to-QUE deterministic intake projection."""
import json
from pathlib import Path

ACTIONABLE = {"ahead-only", "diverged", "unresolved-local-ref", "unrelated-or-unavailable-history"}

def branch_reconciliation_groups(path):
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    if report.get("schema") != "branch-reconciliation-registry/v1":
        raise ValueError("unsupported branch reconciliation schema")
    rows = []
    for row in report.get("branches", []):
        state = row.get("disposition")
        if state not in ACTIONABLE:
            continue
        branch = row["branch"]
        sha = row.get("sha") or "unknown"
        prs = row.get("pull_requests") or []
        pr_refs = [f"#{p['number']} base={p.get('base_ref') or 'unknown'}" for p in prs if p.get("number")]
        detail = "\n".join([
            f"branch={branch}", f"sha={sha}", f"disposition={state}",
            f"ahead={row.get('ahead_of_default')} behind={row.get('behind_default')}",
            "pull_requests=" + (", ".join(pr_refs) if pr_refs else "none"),
            "required=review unique commits, PR base, patch equivalence, checks, ownership and supersession",
        ])
        rows.append({
            "name": branch, "path": "refs/heads/" + branch,
            "key": f"branch:{branch}:{sha[:12]}:{state}",
            "sig": sha[:12], "class": "branch-reconciliation",
            "step": "branch-reconciliation", "priority": 3 if state == "diverged" else 2,
            "detail": detail, "sha": sha,
            "receipts": [{"url": f"https://github.com/timerloggedout-spec/termux-monorepo/commit/{sha}", "sha": sha}],
            "message": state,
        })
    return rows
