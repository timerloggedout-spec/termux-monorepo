#!/usr/bin/env python3
"""Engineering-health snapshot — 100% automated script, zero CellCog/LLM credits.

Pulls dual-gate status, open PR mergeability signals, and recent Actions hygiene
via the GitHub API only. Writes JSON + markdown under --out-dir.

Usage:
  python3 scripts/ci/engineering_health.py
  python3 scripts/ci/engineering_health.py --out-dir /tmp/eng-health
  GITHUB_TOKEN=... python3 scripts/ci/engineering_health.py --repo timerloggedout-spec/termux-monorepo

Env:
  GITHUB_TOKEN or GH_TOKEN — optional; unauthenticated works with low rate limits.
  GITHUB_REPOSITORY — default owner/repo when --repo omitted.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com"
UA = "termux-monorepo-engineering-health/1.0"


def _headers(token: str | None) -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": UA,
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def gh_get(path: str, token: str | None, params: dict[str, str] | None = None) -> Any:
    q = ""
    if params:
        q = "?" + "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params.items())
    url = f"{API}{path}{q}"
    req = urllib.request.Request(url, headers=_headers(token), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"GET {path} -> HTTP {e.code}: {body}") from e


def latest_workflow_run(
    owner: str, repo: str, workflow_file: str, branch: str, token: str | None
) -> dict[str, Any] | None:
    data = gh_get(
        f"/repos/{owner}/{repo}/actions/workflows/{workflow_file}/runs",
        token,
        {"branch": branch, "per_page": "5", "event": "push"},
    )
    runs = data.get("workflow_runs") or []
    return runs[0] if runs else None


def summarize_run(run: dict[str, Any] | None) -> dict[str, Any]:
    if not run:
        return {"status": "missing", "conclusion": None, "html_url": None, "head_sha": None}
    return {
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "html_url": run.get("html_url"),
        "head_sha": (run.get("head_sha") or "")[:12] or None,
        "created_at": run.get("created_at"),
        "display_title": run.get("display_title"),
    }


def gate_label(summary: dict[str, Any]) -> str:
    st, conc = summary.get("status"), summary.get("conclusion")
    if st == "completed" and conc == "success":
        return "green"
    if st == "completed" and conc in ("failure", "timed_out", "cancelled"):
        return "red"
    if st in ("queued", "in_progress", "waiting", "requested", "pending"):
        return "pending"
    if st == "missing":
        return "unknown"
    return "unknown"


def collect(owner: str, repo: str, branch: str, token: str | None) -> dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    repo_meta = gh_get(f"/repos/{owner}/{repo}", token)
    default_branch = repo_meta.get("default_branch") or branch

    repo_gate = summarize_run(
        latest_workflow_run(owner, repo, "repo-gate.yml", default_branch, token)
    )
    termux_smoke = summarize_run(
        latest_workflow_run(owner, repo, "termux-smoke.yml", default_branch, token)
    )

    open_prs = gh_get(
        f"/repos/{owner}/{repo}/pulls",
        token,
        {"state": "open", "sort": "updated", "direction": "desc", "per_page": "30"},
    )
    pr_rows = []
    for pr in open_prs:
        pr_rows.append(
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "draft": bool(pr.get("draft")),
                "mergeable_state": pr.get("mergeable_state"),  # often null on list endpoint
                "html_url": pr.get("html_url"),
                "updated_at": pr.get("updated_at"),
                "user": (pr.get("user") or {}).get("login"),
            }
        )

    recent_runs = gh_get(
        f"/repos/{owner}/{repo}/actions/runs",
        token,
        {"branch": default_branch, "per_page": "15"},
    )
    hygiene = []
    for run in recent_runs.get("workflow_runs") or []:
        hygiene.append(
            {
                "name": run.get("name"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "event": run.get("event"),
                "html_url": run.get("html_url"),
                "head_sha": (run.get("head_sha") or "")[:12],
                "created_at": run.get("created_at"),
            }
        )

    dual = {
        "repo_gate": {**repo_gate, "label": gate_label(repo_gate)},
        "termux_smoke": {**termux_smoke, "label": gate_label(termux_smoke)},
    }
    dual["combined"] = (
        "green"
        if dual["repo_gate"]["label"] == "green" and dual["termux_smoke"]["label"] == "green"
        else "not_green"
    )

    return {
        "schema": "engineering-health/v1",
        "observed_at": now,
        "repository": f"{owner}/{repo}",
        "default_branch": default_branch,
        "head_sha_hint": repo_meta.get("pushed_at"),
        "dual_gates": dual,
        "open_prs": {
            "count": len(pr_rows),
            "items": pr_rows,
        },
        "actions_hygiene": {
            "recent_runs": hygiene,
            "failed_recent": [
                r
                for r in hygiene
                if r.get("status") == "completed"
                and r.get("conclusion") not in (None, "success", "skipped", "neutral")
            ],
        },
        "cellcog_dashboard_ref": {
            "url": "https://cellcog.ai/app/6aa08a02bf7d52bfa976cd2e/dashboard/engineering-health/",
            "note": "Human/optional view only. This script does not call CellCog or burn agent credits.",
        },
        "credit_policy": "zero_cellcog_llm_credits",
    }


def to_markdown(snap: dict[str, Any]) -> str:
    dg = snap["dual_gates"]
    lines = [
        f"# Engineering health — `{snap['repository']}`",
        "",
        f"- **Observed (UTC):** `{snap['observed_at']}`",
        f"- **Default branch:** `{snap['default_branch']}`",
        f"- **Dual gates combined:** **{dg['combined']}**",
        f"- **Credit policy:** `{snap['credit_policy']}` (no CellCog agent calls)",
        "",
        "## Dual gates",
        "",
        f"| Gate | Label | Status | Conclusion | SHA |",
        f"|---|---|---|---|---|",
        f"| repo-gate | {dg['repo_gate']['label']} | {dg['repo_gate']['status']} | {dg['repo_gate']['conclusion']} | `{dg['repo_gate']['head_sha'] or '—'}` |",
        f"| termux-smoke | {dg['termux_smoke']['label']} | {dg['termux_smoke']['status']} | {dg['termux_smoke']['conclusion']} | `{dg['termux_smoke']['head_sha'] or '—'}` |",
        "",
        f"## Open PRs ({snap['open_prs']['count']})",
        "",
    ]
    if not snap["open_prs"]["items"]:
        lines.append("_None._")
    else:
        lines.append("| # | Title | Draft | Updated |")
        lines.append("|---|---|---|---|")
        for p in snap["open_prs"]["items"][:20]:
            title = (p.get("title") or "").replace("|", "\\|")[:60]
            lines.append(
                f"| [{p['number']}]({p['html_url']}) | {title} | {p['draft']} | {p.get('updated_at') or '—'} |"
            )
    failed = snap["actions_hygiene"]["failed_recent"]
    lines.extend(["", "## Recent Actions failures (branch)", ""])
    if not failed:
        lines.append("_No failed runs in recent window._")
    else:
        for r in failed[:10]:
            lines.append(
                f"- **{r.get('name')}** `{r.get('conclusion')}` — {r.get('html_url')}"
            )
    ref = snap["cellcog_dashboard_ref"]
    lines.extend(
        [
            "",
            "## CellCog dashboard (optional human view)",
            "",
            f"- URL: {ref['url']}",
            f"- {ref['note']}",
            "",
        ]
    )
    return "\n".join(lines) + "\n"

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo"),
        help="owner/repo",
    )
    p.add_argument("--branch", default="", help="unused; uses default_branch from API")
    p.add_argument(
        "--out-dir",
        default=os.environ.get("ENGINEERING_HEALTH_OUT", "engineering-health-out"),
        help="directory for snapshot.json and snapshot.md",
    )
    args = p.parse_args()
    if "/" not in args.repo:
        print("--repo must be owner/repo", file=sys.stderr)
        return 2
    owner, repo = args.repo.split("/", 1)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None

    snap = collect(owner, repo, args.branch or "master", token)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "snapshot.json").write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    md = to_markdown(snap)
    (out / "snapshot.md").write_text(md, encoding="utf-8")

    print(md)
    print(f"Wrote {out / 'snapshot.json'} and {out / 'snapshot.md'}", file=sys.stderr)
    # Non-zero only on hard API failure (already raised). Always 0 for red gates — report, don't fail CI by default.
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"::error::engineering_health failed: {e}", file=sys.stderr)
        raise SystemExit(1)
