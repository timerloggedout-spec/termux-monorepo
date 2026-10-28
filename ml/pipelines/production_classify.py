"""Production run of the vocab-v2 PR classifier over the live open-PR list.

The keep-alive workflow only exercises this package's unit tests when
ml/** paths change; nothing else has ever run classify_pr against the
real PR stream (recon: docs/ops/TIER1-CLASSIFIER-RECON-2026-10-28.md,
gap 1). This collector closes that gap the way the fleet's other
collectors work: a scheduled workflow runs it, and it writes a committed
feed (ops/ml/pr-lane-feed.json) that any surface can consume.

Input mapping (GitHub pulls API -> classify_pr dict):
  title/draft/mergeable_state/base.ref/user.login  <- PR object (detail GET)
  changed_files                                    <- PR detail GET
  age_days                                         <- now - created_at
  gates.repo-gate     <- a completed check run named
                         "hygiene + portability gate" with conclusion
                         "success" on the PR head sha
  gates.termux-smoke  <- same for "agentic termux smoke"
  wholesale / keep_alive / product                 <- False (session-only
                         signals in the fixture era; no live source)
  why                                              <- "" (same)

A PR whose gate checks have not run gets gates={} and lands in
NEED_EVIDENCE — the classifier's own verdict for missing evidence,
not a collector error.

Network lives in main() only; build_pr_dict / classify_all are pure and
unit-tested (ml/pipelines/test_production_classify.py).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml.pipelines.lanes.classify import classify_pr  # noqa: E402

API = "https://api.github.com"
GATE_CHECKS = {"repo-gate": "hygiene + portability gate",
               "termux-smoke": "agentic termux smoke"}
FEED_SCHEMA = "pr-lane-feed/v1"


def _parse_ts(raw: str) -> datetime:
    return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def build_pr_dict(pr: dict[str, Any], checks: list[dict[str, Any]],
                  now: datetime) -> dict[str, Any]:
    """Map one GitHub PR object + its head check runs to the classifier dict."""
    gates: dict[str, bool] = {}
    for key, check_name in GATE_CHECKS.items():
        gates[key] = any(
            c.get("name") == check_name and c.get("conclusion") == "success"
            for c in checks
        )
    created = _parse_ts(pr["created_at"])
    return {
        "number": pr["number"],
        "title": pr.get("title") or "",
        "base": {"ref": (pr.get("base") or {}).get("ref")},
        "user": {"login": (pr.get("user") or {}).get("login")},
        "draft": bool(pr.get("draft")),
        "mergeable_state": pr.get("mergeable_state") or "unknown",
        "changed_files": pr.get("changed_files") or 0,
        "age_days": max(0.0, (now - created).total_seconds() / 86400.0),
        "gates": gates,
        "wholesale": False,
        "keep_alive": False,
        "product": False,
        "why": "",
    }


def classify_all(pr_dicts: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    """Classify mapped PR dicts and build the feed payload."""
    rows = []
    counts: dict[str, int] = {}
    for d in pr_dicts:
        lane = classify_pr(d).value
        counts[lane] = counts.get(lane, 0) + 1
        rows.append({
            "number": d["number"],
            "title": d["title"],
            "author": (d.get("user") or {}).get("login"),
            "draft": d["draft"],
            "age_days": round(float(d.get("age_days") or 0), 1),
            "changed_files": d["changed_files"],
            "gates": d["gates"],
            "lane": lane,
        })
    rows.sort(key=lambda r: r["number"])
    return {
        "schema": FEED_SCHEMA,
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "open_prs": len(rows),
        "counts": dict(sorted(counts.items())),
        "prs": rows,
    }


def _get(path: str, token: str) -> Any:
    req = urllib.request.Request(
        API + path,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "ml-pr-lane-classify"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def _get_or(path: str, token: str, default: Any, warnings: list[str]) -> Any:
    """GET with a recorded fallback. Per-PR fetches must not kill the run:
    a fork PR whose head sha is unreachable 404s its check-runs, and one
    bad PR must degrade to missing evidence, not a failed production run
    (first dispatched run 40779970361 died exactly this way)."""
    try:
        return _get(path, token)
    except Exception as exc:  # HTTPError and transport errors alike
        warnings.append(f"{path}: {exc}")
        return default


def main() -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("::error::GH_TOKEN/GITHUB_TOKEN not set in this environment", flush=True)
        return 1
    print("::notice::classify run starting", flush=True)
    try:
        return _run(token)
    except Exception as exc:
        print(f"::error::classify failed: {type(exc).__name__}: {exc}", flush=True)
        # Job logs and workflow-command annotations have proven unreadable
        # through the fleet's API route (runs 40779970361/40780377727/
        # 40780704752 left no trace), so the failure record goes in the
        # feed itself — the workflow commits it with if: always(). An
        # error feed on master is more honest than a stale one.
        out_path = os.environ.get(
            "PR_LANE_FEED",
            os.path.join(os.path.dirname(__file__), "..", "..", "ops", "ml", "pr-lane-feed.json"),
        )
        payload = {
            "schema": FEED_SCHEMA,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "open_prs": 0,
            "counts": {},
            "prs": [],
            "error": f"{type(exc).__name__}: {exc}",
        }
        try:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w") as fh:
                json.dump(payload, fh, indent=1)
                fh.write("\n")
        except Exception:
            pass
        return 1


def _run(token: str) -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")
    out_path = os.environ.get(
        "PR_LANE_FEED",
        os.path.join(os.path.dirname(__file__), "..", "..", "ops", "ml", "pr-lane-feed.json"),
    )
    now = datetime.now(timezone.utc)
    pr_dicts: list[dict[str, Any]] = []
    warnings: list[str] = []
    page = 1
    while True:
        try:
            batch = _get(f"/repos/{repo}/pulls?state=open&per_page=100&page={page}", token)
        except Exception as exc:
            # Fail closed (an empty feed would be a false classification),
            # but name the cause in an annotation — job logs are not
            # API-readable, annotations are.
            print(f"::error::open-PR list fetch failed: {exc}", flush=True)
            raise
        print(f"::notice::page {page}: {len(batch)} PR stubs", flush=True)
        if not batch:
            break
        for stub in batch:
            pr = _get_or(f"/repos/{repo}/pulls/{stub['number']}", token, None, warnings)
            if pr is None:
                continue
            checks_page = _get_or(
                f"/repos/{repo}/commits/{pr['head']['sha']}/check-runs?per_page=100",
                token, {}, warnings)
            pr_dicts.append(build_pr_dict(pr, checks_page.get("check_runs", []), now))
        if len(batch) < 100:
            break
        page += 1
    for warning in warnings:
        print(f"::warning::fetch degraded: {warning}", flush=True)
    print(f"::notice::mapped {len(pr_dicts)} PRs, classifying", flush=True)
    feed = classify_all(pr_dicts, now)
    feed["fetch_warnings"] = len(warnings)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(feed, fh, indent=1)
        fh.write("\n")
    print(f"classified {feed['open_prs']} open PRs: {feed['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
