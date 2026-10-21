"""Optional network collector using `gh api` (GITHUB_TOKEN / gh auth)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _gh_api(path: str, *, paginate: bool = False) -> Any:
    cmd = ["gh", "api", path]
    if paginate:
        cmd.append("--paginate")
    env = os.environ.copy()
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"gh api failed ({r.returncode}): {r.stderr.strip()[:500]}")
    text = r.stdout.strip()
    if not text:
        return None
    # paginate may emit NDJSON-ish concatenated JSON objects — try whole then lines
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        items: list[Any] = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                items.append(json.loads(line))
        return items


def _write_json(path: Path, data: Any, meta: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collector_version": "0.1.0",
        "meta": meta,
        "data": data,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def collect_main(args: Any) -> int:
    owner, repo = args.owner, args.repo
    out: Path = args.out
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = f"repos/{owner}/{repo}"

    try:
        runs_path = f"{base}/actions/runs?per_page={min(args.max_runs, 100)}"
        if args.workflow:
            # resolve workflow id by filename is multi-step; filter client-side
            pass
        runs = _gh_api(runs_path)
    except Exception as e:
        print(f"collect: runs failed: {e}", file=sys.stderr)
        return 2

    workflow_runs = []
    if isinstance(runs, dict):
        workflow_runs = list(runs.get("workflow_runs") or [])
    elif isinstance(runs, list):
        workflow_runs = runs

    if args.workflow:
        wf = args.workflow.lower()
        workflow_runs = [
            r
            for r in workflow_runs
            if wf in str(r.get("path") or "").lower()
            or wf in str(r.get("name") or "").lower()
        ]
    workflow_runs = workflow_runs[: args.max_runs]

    runs_file = out / "actions-runs" / f"runs-{stamp}.json"
    _write_json(
        runs_file,
        {"workflow_runs": workflow_runs, "count": len(workflow_runs)},
        {"endpoint": runs_path, "owner": owner, "repo": repo},
    )
    print(f"wrote {runs_file} ({len(workflow_runs)} runs)")

    if args.with_jobs:
        jobs_dir = out / "actions-jobs" / stamp
        jobs_dir.mkdir(parents=True, exist_ok=True)
        for r in workflow_runs:
            rid = r.get("id")
            if rid is None:
                continue
            try:
                jobs = _gh_api(f"{base}/actions/runs/{rid}/jobs")
            except Exception as e:
                print(f"collect: jobs {rid} failed: {e}", file=sys.stderr)
                continue
            jf = jobs_dir / f"jobs-{rid}.json"
            _write_json(jf, jobs, {"run_id": rid, "endpoint": f".../runs/{rid}/jobs"})
        print(f"wrote jobs under {jobs_dir}")

    if args.with_stats:
        for name, ep in [
            ("commit_activity", f"{base}/stats/commit_activity"),
            ("code_frequency", f"{base}/stats/code_frequency"),
        ]:
            try:
                data = _gh_api(ep)
                _write_json(
                    out / "repository-stats" / f"{name}-{stamp}.json",
                    data,
                    {"endpoint": ep},
                )
                print(f"wrote stats {name}")
            except Exception as e:
                print(f"collect: {name} failed: {e}", file=sys.stderr)

    if args.with_traffic:
        for name in ("views", "clones", "popular/paths", "popular/referrers"):
            ep = f"{base}/traffic/{name}"
            try:
                data = _gh_api(ep)
                safe = name.replace("/", "-")
                _write_json(
                    out / "traffic" / f"{safe}-{stamp}.json",
                    data,
                    {"endpoint": ep},
                )
                print(f"wrote traffic {name}")
            except Exception as e:
                print(f"collect: traffic {name} failed: {e}", file=sys.stderr)

    return 0
