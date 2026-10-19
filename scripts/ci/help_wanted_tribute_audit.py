#!/usr/bin/env python3
"""Automated, read-only audit of Help-Wanted tribute lifecycle evidence.

Never infers validation, acceptance, or realized effect from a claim/receipt alone.
Rate limits and missing data are recorded as unknown rather than success.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com"
STAKE_PATH = ".github/help-wanted-lane-stake.md"
SOLUTION_PROOF = ("### Help-Given Tribute", "- Stage: solution", "- Diff proof:", "- Validation:")
SUCCESS_CONCLUSIONS = {"success", "skipped", "neutral"}


def api_get(path: str) -> tuple[Any | None, str | None]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-help-wanted-tribute-audit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = (
        os.environ.get("OPERATOR_GITHUB_TOKEN")
        or os.environ.get("OPERATOR_TOKEN")
        or os.environ.get("ARCHWIZ_GITHUB_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or ""
    )
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(path if path.startswith("http") else API + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode()), None
    except urllib.error.HTTPError as error:
        headers = error.headers or {}
        try:
            body = error.read().decode(errors="ignore").lower()
        except OSError:
            body = ""
        rate_limited = error.code == 429 or (
            error.code == 403 and (
                str(headers.get("X-RateLimit-Remaining", "")) == "0"
                or bool(headers.get("Retry-After"))
                or any(marker in body for marker in (
                    "rate limit", "secondary rate limit", "abuse detection"
                ))
            )
        )
        return None, "rate_limited" if rate_limited else f"http_{error.code}"
    except (OSError, TimeoutError, json.JSONDecodeError) as error:
        return None, type(error).__name__


def parse_pr_url(url: str) -> tuple[str, str, int] | None:
    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)/?", url.strip())
    if not match:
        return None
    return match.group(1), match.group(2), int(match.group(3))


def audit_one(pr_url: str) -> dict[str, Any]:
    parsed = parse_pr_url(pr_url)
    base: dict[str, Any] = {
        "pr_url": pr_url,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "stage": "unknown",
        "evidence_gaps": [],
        "realized_effect_verified": False,
    }
    if not parsed:
        base["evidence_gaps"].append("invalid_pr_url")
        return base

    owner, repo, number = parsed
    pr, error = api_get(f"/repos/{owner}/{repo}/pulls/{number}")
    if not isinstance(pr, dict):
        base["evidence_gaps"].append(error or "pull_request_unavailable")
        base["audit_status"] = "deferred" if error == "rate_limited" else "unknown"
        return base

    files, files_error = api_get(f"/repos/{owner}/{repo}/pulls/{number}/files?per_page=100")
    checks = None
    head_sha = (pr.get("head") or {}).get("sha")
    if head_sha:
        checks, checks_error = api_get(f"/repos/{owner}/{repo}/commits/{head_sha}/check-runs?per_page=100")
    else:
        checks_error = "head_sha_missing"

    names = [str(row.get("filename") or "") for row in files] if isinstance(files, list) else []
    changed = [
        row for row in (files if isinstance(files, list) else [])
        if (int(row.get("additions") or 0) + int(row.get("deletions") or 0)) > 0
    ]
    implementation_files = [row for row in changed if row.get("filename") != STAKE_PATH]
    body = str(pr.get("body") or "")
    proof_present = all(marker in body for marker in SOLUTION_PROOF)
    stake_only = bool(changed) and not implementation_files
    check_rows = (checks or {}).get("check_runs", []) if isinstance(checks, dict) else []
    checks_total_count = (checks or {}).get("total_count", len(check_rows)) if isinstance(checks, dict) else 0
    checks_truncated = isinstance(checks, dict) and checks_total_count > len(check_rows)
    checks_complete = bool(check_rows) and not checks_truncated and all(
        row.get("status") == "completed" for row in check_rows
    )
    checks_pass = (
        checks_complete
        and any(row.get("conclusion") == "success" for row in check_rows)
        and all(row.get("conclusion") in SUCCESS_CONCLUSIONS for row in check_rows)
    )

    base.update({
        "audit_status": "partial" if files_error or checks_error else "observed",
        "state": pr.get("state"),
        "merged": bool(pr.get("merged_at")),
        "head_sha": head_sha,
        "base_sha": (pr.get("base") or {}).get("sha"),
        "changed_file_count": len(changed),
        "implementation_file_count": len(implementation_files),
        "stake_marker_present": STAKE_PATH in names,
        "stake_only": stake_only,
        "solution_proof_present": proof_present,
        "checks_observed": len(check_rows),
        "checks_total_count": checks_total_count,
        "checks_truncated": checks_truncated,
        "checks_complete": checks_complete,
        "checks_pass": checks_pass,
    })

    if files_error:
        base["evidence_gaps"].append(f"files_{files_error}")
    if checks_error:
        base["evidence_gaps"].append(f"checks_{checks_error}")
    if checks_truncated:
        base["evidence_gaps"].append("checks_truncated")
    if not changed:
        base["evidence_gaps"].append("implementation_delta_not_observed")
    if not proof_present:
        base["evidence_gaps"].append("solution_proof_missing")
    if not checks_pass:
        base["evidence_gaps"].append("validation_not_verified")

    if pr.get("merged_at"):
        base["stage"] = "accepted"
    elif pr.get("state") == "closed":
        base["stage"] = "closed_unmerged"
    elif stake_only:
        base["stage"] = "stake_only"
    elif implementation_files and proof_present and checks_pass:
        base["stage"] = "validated_solution"
    elif implementation_files and proof_present:
        base["stage"] = "solution_claimed_unvalidated"
    elif implementation_files:
        base["stage"] = "implementation_unproven"
    else:
        base["stage"] = "unknown"

    # A merge is not, by itself, proof of downstream realized effect.
    base["realized_effect_verified"] = False
    base["realization_note"] = "requires a separately linked, independently verified effect receipt"
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default="docs/ops/generated/help-wanted-status.json")
    parser.add_argument("--out", default="docs/ops/generated/help-wanted-tribute-audit.json")
    parser.add_argument("--dashboard", default="apps/help-wanted-dashboard/data/status.json")
    parser.add_argument("--max-prs", type=int, default=25)
    args = parser.parse_args()

    status_path = Path(args.status)
    board = json.loads(status_path.read_text(encoding="utf-8"))
    tributes = board.get("tributes") or []
    urls = []
    for tribute in tributes:
        url = str(tribute.get("pr_url") or "")
        if url and url not in urls:
            urls.append(url)
    batch_size = max(0, args.max_prs)
    if batch_size and len(urls) > batch_size:
        # Rotate the bounded audit window hourly so old entries are not starved.
        hour = int(datetime.now(timezone.utc).timestamp() // 3600)
        start = (hour * batch_size) % len(urls)
        selected = [urls[(start + offset) % len(urls)] for offset in range(min(batch_size, len(urls)))]
    else:
        start = 0
        selected = urls[:batch_size]
    results = [audit_one(url) for url in selected]
    stages = Counter(row["stage"] for row in results)
    statuses = Counter(row.get("audit_status", "observed") for row in results)
    report = {
        "schema_version": "help-wanted.tribute-audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_status_generated_at": board.get("generated_at"),
        "source_tribute_count": len(tributes),
        "unique_pr_count": len(urls),
        "audited_pr_count": len(results),
        "not_audited_count": max(0, len(urls) - len(results)),
        "audit_window_start": start,
        "audit_window_size": batch_size,
        "stages": dict(stages),
        "audit_statuses": dict(statuses),
        "realized_effect_verified_count": sum(bool(row.get("realized_effect_verified")) for row in results),
        "policy": {
            "claim_is_solution": False,
            "merge_is_realized_effect": False,
            "missing_evidence_is_success": False,
            "audit_is_read_only": True,
        },
        "items": results,
    }
    board["tribute_audit"] = report
    serialized_board = json.dumps(board, indent=2) + "\n"
    status_path.write_text(serialized_board, encoding="utf-8")
    dashboard_path = Path(args.dashboard)
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(serialized_board, encoding="utf-8")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "audited": len(results),
        "unique_prs": len(urls),
        "stages": dict(stages),
        "realized_effect_verified": report["realized_effect_verified_count"],
        "output": str(out_path),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
