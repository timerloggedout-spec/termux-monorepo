#!/usr/bin/env python3
"""Build a deterministic, redacted temporal context/lead-lag index from GitHub event data."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from archwiz.context_relationships.evidence_matrix import project_evidence_matrix


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def decode_gh_json(output: str, *, label: str) -> object:
    """Decode one JSON document and give the caller a source-specific failure."""
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} returned invalid JSON: {exc}") from exc


def run_gh(*args: str, paginate: bool = False) -> object:
    """Run a read-only GitHub CLI query.

    GitHub CLI writes one JSON document per page with ``--paginate`` unless
    ``--slurp`` is also supplied.  Always request slurped pages here so callers
    receive a single parseable outer array; this prevents a successful audit
    from silently losing check evidence through concatenated JSON output.
    """
    env = os.environ.copy()
    # CI may inherit terminal colour/TTY variables from a wrapper.  API responses
    # are an artifact contract, so force uncoloured non-interactive JSON rather
    # than trying to strip control bytes after retrieval.
    env["GH_PAGER"] = "cat"
    env["PAGER"] = "cat"
    env["NO_COLOR"] = "1"
    env["CLICOLOR"] = "0"
    env.pop("CLICOLOR_FORCE", None)
    env.pop("GH_FORCE_TTY", None)
    command = ["gh", *args]
    if paginate:
        command.extend(["--paginate", "--slurp"])
    output = subprocess.check_output(command, env=env, text=True)
    return decode_gh_json(output, label="gh api" if paginate else "gh")


def normalize_paginated(payload: object, *, item_key: str | None = None, label: str) -> list[dict[str, Any]]:
    """Flatten ``gh api --paginate --slurp`` pages with an explicit endpoint shape."""
    if not isinstance(payload, list):
        raise ValueError(f"{label} paginated response must be a slurped array of pages")
    items: list[dict[str, Any]] = []
    for index, page in enumerate(payload):
        if item_key is None:
            page_items = page
        elif isinstance(page, dict):
            page_items = page.get(item_key)
        else:
            raise ValueError(f"{label} page {index} must be an object containing {item_key!r}")
        if not isinstance(page_items, list):
            expected = "an array" if item_key is None else f"an array at {item_key!r}"
            raise ValueError(f"{label} page {index} must contain {expected}")
        for item in page_items:
            if not isinstance(item, dict):
                raise ValueError(f"{label} page {index} contains a non-object item")
            items.append(item)
    return items


def load_optional_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return parsed


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seconds_between(a: str | None, b: str | None) -> float | None:
    left, right = parse_time(a), parse_time(b)
    if not left or not right:
        return None
    return max(0.0, (right - left).total_seconds())


def classify_event(event: dict[str, Any]) -> str:
    kind = event.get("event") or event.get("type") or "unknown"
    action = event.get("action") or ""
    return f"{kind}:{action}" if action else str(kind)


def optional_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SystemExit(f"invalid integer: {value!r}") from exc
    if parsed < 1:
        raise SystemExit("number must be positive")
    return parsed


def warning(kind: str, observed_at: str, exc: Exception) -> dict[str, str]:
    """Represent collection failure as non-evidence without persisting raw CLI output."""
    return {
        "kind": kind,
        "observed_at": observed_at,
        "classification": "WARNING",
        "outcome": "UNKNOWN",
        "error_class": type(exc).__name__,
        "error_digest": hashlib.sha256(str(exc).encode("utf-8")).hexdigest()[:20],
    }


def correlatable_lead(event: dict[str, Any]) -> bool:
    return not str(event.get("kind", "")).endswith("_warning")


def correlatable_lag(event: dict[str, Any]) -> bool:
    return event.get("kind") in {"check", "merge", "close"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evaluation-results/context-relationship-index.json")
    parser.add_argument("--pr")
    parser.add_argument("--issue")
    parser.add_argument("--head-sha", default=os.getenv("GITHUB_SHA", ""))
    parser.add_argument(
        "--graph-summary",
        type=Path,
        default=Path("workspace/llm_map/context_relationships/build-summary.json"),
        help="Optional checked-in canonical graph coverage summary; never a graph writer input.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event = json.loads(Path(event_path).read_text()) if event_path and Path(event_path).exists() else {}
    observed_at = now()

    pr_number = optional_int(args.pr) or event.get("pull_request", {}).get("number")
    issue_number = optional_int(args.issue) or event.get("issue", {}).get("number")
    head_sha = args.head_sha or event.get("pull_request", {}).get("head", {}).get("sha") or event.get("after", "")

    lead_events: list[dict[str, Any]] = [{
        "kind": "github_event",
        "class": classify_event(event),
        "observed_at": observed_at,
        "event_name": os.getenv("GITHUB_EVENT_NAME", "unknown"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "head_sha": head_sha,
    }]
    lag_events: list[dict[str, Any]] = []

    if repo and pr_number:
        try:
            pr = run_gh(
                "pr", "view", str(pr_number), "--repo", repo,
                "--json", "number,headRefOid,createdAt,updatedAt,mergedAt,closedAt,state",
            )
            if not isinstance(pr, dict):
                raise ValueError("pull-request query returned a non-object response")
            lead_events.append({"kind": "pull_request", "number": pr["number"], "observed_at": observed_at,
                                "source_sha": pr.get("headRefOid"), "created_at": pr.get("createdAt")})
            if pr.get("mergedAt"):
                lag_events.append({"kind": "merge", "observed_at": pr["mergedAt"], "source_sha": pr.get("headRefOid")})
            elif pr.get("closedAt"):
                lag_events.append({"kind": "close", "observed_at": pr["closedAt"], "source_sha": pr.get("headRefOid")})
        except Exception as exc:
            lead_events.append(warning("pr_query_warning", observed_at, exc))

    if repo and (pr_number or issue_number):
        number = pr_number or issue_number
        try:
            comment_pages = run_gh("api", f"repos/{repo}/issues/{number}/comments", paginate=True)
            comments = normalize_paginated(comment_pages, label="comments")
            for comment in comments[-100:]:
                lead_events.append({
                    "kind": "comment",
                    "id": comment.get("id"),
                    "created_at": comment.get("created_at"),
                    "updated_at": comment.get("updated_at"),
                    "author": comment.get("user", {}).get("login"),
                })
        except Exception as exc:
            lead_events.append(warning("comment_query_warning", observed_at, exc))

    if repo and head_sha:
        try:
            check_pages = run_gh("api", f"repos/{repo}/commits/{head_sha}/check-runs", paginate=True)
            checks = normalize_paginated(check_pages, item_key="check_runs", label="check-runs")
            for check in checks:
                lag_events.append({
                    "kind": "check",
                    "name": check.get("name"),
                    "status": check.get("status"),
                    "conclusion": check.get("conclusion"),
                    "started_at": check.get("started_at"),
                    "completed_at": check.get("completed_at"),
                    "run_id": check.get("id"),
                })
        except Exception as exc:
            lag_events.append(warning("check_query_warning", observed_at, exc))

    pairs = []
    for lead in lead_events:
        if not correlatable_lead(lead):
            continue
        lead_time = lead.get("observed_at") or lead.get("created_at")
        candidates = []
        for lag in lag_events:
            if not correlatable_lag(lag):
                continue
            lag_time = lag.get("observed_at") or lag.get("completed_at") or lag.get("started_at")
            delta = seconds_between(lead_time, lag_time)
            if delta is not None and delta >= 0:
                candidates.append((delta, lag))
        if candidates:
            delta, lag = min(candidates, key=lambda item: item[0])
            pairs.append({
                "lead_kind": lead.get("kind"),
                "lag_kind": lag.get("kind"),
                "lead_at": lead_time,
                "lag_at": lag.get("observed_at") or lag.get("completed_at") or lag.get("started_at"),
                "elapsed_seconds": delta,
                "relationship_status": "temporal-correlation",
                "causal_claim": False,
            })

    result: dict[str, Any] = {
        "schema": "context-relationship-index/v1",
        "observed_at": observed_at,
        "repository": repo,
        "source_sha": head_sha,
        "event_name": os.getenv("GITHUB_EVENT_NAME", "unknown"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "correlation": {"pr_number": pr_number, "issue_number": issue_number,
                        "context_key": os.getenv("CONTEXT_KEY"), "experiment_id": os.getenv("EXPERIMENT_ID")},
        "lead_events": lead_events,
        "lag_events": lag_events,
        "lead_lag_pairs": pairs,
        "limitations": [
            "Temporal correlation is not causal attribution.",
            "GitHub login is not sufficient to identify the underlying agent when a shared PAT is used.",
            "Missing provider/session provenance remains INCONCLUSIVE rather than being guessed.",
            "Collector WARNING/UNKNOWN records are not successful check evidence and are excluded from temporal pairs.",
        ],
    }
    result["evidence_matrix"] = project_evidence_matrix(result, load_optional_json(args.graph_summary))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {out} with {len(lead_events)} leads, {len(lag_events)} lags, "
        f"{len(pairs)} temporal pairs, and {len(result['evidence_matrix']['records'])} matrix records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
