#!/usr/bin/env python3
"""Build an append-only GitHub history correlation ledger.

The ledger is deliberately evidence-oriented: GitHub object IDs, SHAs, refs,
workflow/run/job/artifact IDs and timestamps are join keys. It does not infer
correctness from telemetry. Repeated scheduled observations allow downstream
BIUDL/effectiveness consumers to accumulate history without rewriting evidence.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
from typing import Any

API = "https://api.github.com"
HEADERS_BASE = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "termux-monorepo-historical-correlation",
}


def get(path: str, token: str) -> Any:
    req = urllib.request.Request(
        API + path,
        headers={**HEADERS_BASE, "Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def paged(path: str, token: str, pages: int) -> tuple[list[Any], str | None]:
    out: list[Any] = []
    for page in range(1, pages + 1):
        sep = "&" if "?" in path else "?"
        try:
            batch = get(f"{path}{sep}per_page=100&page={page}", token)
        except Exception as exc:  # Preserve partial evidence; do not erase prior data.
            return out, f"{type(exc).__name__}: {exc}"
        if not isinstance(batch, list) or not batch:
            break
        out.extend(batch)
        if len(batch) < 100:
            break
    return out, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--out", default="artifacts/github-history")
    parser.add_argument("--pages", type=int, default=3)
    parser.add_argument("--nested-pages", type=int, default=1)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token or not args.repo:
        raise SystemExit("GITHUB_TOKEN and --repo are required")

    root = pathlib.Path(args.out)
    root.mkdir(parents=True, exist_ok=True)
    observed = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    errors: list[dict[str, str]] = []
    repo = args.repo

    # Global collections cover the historical object classes that can be
    # correlated without first knowing a parent PR/issue.
    endpoints = {
        "commits": f"/repos/{repo}/commits",
        "issues": f"/repos/{repo}/issues?state=all&sort=updated&direction=desc",
        "pulls": f"/repos/{repo}/pulls?state=all&sort=updated&direction=desc",
        "runs": f"/repos/{repo}/actions/runs",
        "branches": f"/repos/{repo}/branches",
        "issue_comments": f"/repos/{repo}/issues/comments?sort=updated&direction=desc",
        "review_comments": f"/repos/{repo}/pulls/comments?sort=updated&direction=desc",
    }

    data: dict[str, Any] = {
        "schema": "github-history-correlation/v2",
        "observed_at": observed,
        "repository": repo,
        "entities": {},
    }

    def collect(name_path: tuple[str, str]) -> tuple[str, list[Any], str | None]:
        name, path = name_path
        rows, err = paged(path, token, args.pages)
        return name, rows, err

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for name, rows, err in pool.map(collect, endpoints.items()):
            data["entities"][name] = rows
            if err:
                errors.append({"entity": name, "error": err})

    # Parent-scoped reviews and Actions execution detail are the important
    # second-order edges: PR -> review/review-comment and run -> job -> step/artifact.
    pulls = data["entities"].get("pulls", [])
    runs = data["entities"].get("runs", [])

    review_targets = [p.get("number") for p in pulls if p.get("number") is not None]
    run_targets = [r.get("id") for r in runs if r.get("id") is not None]

    def collect_reviews(number: int) -> tuple[str, int, list[Any], str | None]:
        rows, err = paged(f"/repos/{repo}/pulls/{number}/reviews", token, args.nested_pages)
        return "reviews", number, rows, err

    def collect_run_detail(run_id: int) -> tuple[int, list[Any], list[Any], dict[int, list[Any]], list[dict[str, str]]]:
        local_errors: list[dict[str, str]] = []
        jobs, err = paged(f"/repos/{repo}/actions/runs/{run_id}/jobs", token, args.nested_pages)
        if err:
            local_errors.append({"entity": f"run:{run_id}:jobs", "error": err})
        artifacts, err = paged(f"/repos/{repo}/actions/runs/{run_id}/artifacts", token, args.nested_pages)
        if err:
            local_errors.append({"entity": f"run:{run_id}:artifacts", "error": err})
        steps: dict[int, list[Any]] = {}
        # Step summaries are fetched separately because the connector/API shape
        # exposes them on the job endpoint; keep a normalized step collection.
        for job in jobs:
            jid = job.get("id")
            if jid is None:
                continue
            try:
                detail = get(f"/repos/{repo}/actions/jobs/{jid}", token)
                steps[jid] = detail.get("steps", []) if isinstance(detail, dict) else []
            except Exception as exc:
                local_errors.append({"entity": f"job:{jid}:steps", "error": f"{type(exc).__name__}: {exc}"})
        return run_id, jobs, artifacts, steps, local_errors

    data["entities"]["reviews"] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for _, number, rows, err in pool.map(collect_reviews, review_targets):
            data["entities"]["reviews"][str(number)] = rows
            if err:
                errors.append({"entity": f"reviews:{number}", "error": err})

    data["entities"]["run_jobs"] = {}
    data["entities"]["run_artifacts"] = {}
    data["entities"]["job_steps"] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for run_id, jobs, artifacts, steps, local_errors in pool.map(collect_run_detail, run_targets):
            data["entities"]["run_jobs"][str(run_id)] = jobs
            data["entities"]["run_artifacts"][str(run_id)] = artifacts
            for job_id, rows in steps.items():
                data["entities"]["job_steps"][str(job_id)] = rows
            errors.extend(local_errors)

    # Stable, explicit edges. Consumers can join these without trusting display
    # names, ordering, or inferred causal relationships.
    edges: list[dict[str, Any]] = []
    for pr in pulls:
        number = pr.get("number")
        edges.extend([
            {"type": "pr_head", "pr": number, "sha": (pr.get("head") or {}).get("sha"), "updated_at": pr.get("updated_at")},
            {"type": "pr_base", "pr": number, "sha": (pr.get("base") or {}).get("sha")},
        ])
        for review in data["entities"]["reviews"].get(str(number), []):
            edges.append({"type": "pr_review", "pr": number, "review_id": review.get("id"), "commit_id": review.get("commit_id"), "state": review.get("state"), "submitted_at": review.get("submitted_at")})

    for comment in data["entities"].get("issue_comments", []):
        edges.append({"type": "issue_comment", "comment_id": comment.get("id"), "issue_or_pr": comment.get("issue_url", "").rstrip("/").split("/")[-1], "updated_at": comment.get("updated_at")})
    for comment in data["entities"].get("review_comments", []):
        edges.append({"type": "review_comment", "comment_id": comment.get("id"), "pr": comment.get("pull_request_url", "").rstrip("/").split("/")[-1], "commit_id": comment.get("commit_id"), "updated_at": comment.get("updated_at")})

    for run in runs:
        run_id = run.get("id")
        edges.append({"type": "workflow_run", "run_id": run_id, "sha": run.get("head_sha"), "workflow": run.get("name"), "workflow_id": run.get("workflow_id"), "status": run.get("status"), "conclusion": run.get("conclusion"), "event": run.get("event"), "created_at": run.get("created_at"), "updated_at": run.get("updated_at")})
        for job in data["entities"]["run_jobs"].get(str(run_id), []):
            jid = job.get("id")
            edges.append({"type": "run_job", "run_id": run_id, "job_id": jid, "status": job.get("status"), "conclusion": job.get("conclusion"), "started_at": job.get("started_at"), "completed_at": job.get("completed_at")})
            for step in data["entities"]["job_steps"].get(str(jid), []):
                edges.append({"type": "job_step", "job_id": jid, "step_number": step.get("number"), "name": step.get("name"), "status": step.get("status"), "conclusion": step.get("conclusion"), "started_at": step.get("started_at"), "completed_at": step.get("completed_at")})
        for artifact in data["entities"]["run_artifacts"].get(str(run_id), []):
            edges.append({"type": "run_artifact", "run_id": run_id, "artifact_id": artifact.get("id"), "name": artifact.get("name"), "size_in_bytes": artifact.get("size_in_bytes"), "expired": artifact.get("expired")})

    for commit in data["entities"].get("commits", []):
        edges.append({"type": "commit", "sha": commit.get("sha"), "message": (commit.get("commit") or {}).get("message", "").splitlines()[0], "author": (commit.get("author") or {}).get("login")})

    data["edges"] = edges
    data["errors"] = errors
    (root / "snapshot.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "observed_at": observed,
        "repository": repo,
        "schema": data["schema"],
        "counts": {k: (len(v) if isinstance(v, (list, dict)) else 0) for k, v in data["entities"].items()},
        "edge_count": len(edges),
        "error_count": len(errors),
    }
    with (root / "receipts.ndjson").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(receipt, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
