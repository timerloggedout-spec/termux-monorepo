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


def merge_audit_history(
    current_urls: list[str], previous_items: list[dict[str, Any]], fresh_items: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Keep the latest known evidence for every current PR across rotating runs."""
    allowed = set(current_urls)
    merged = {
        str(row.get("pr_url")): row
        for row in previous_items
        if isinstance(row, dict) and row.get("pr_url") in allowed
    }
    for row in fresh_items:
        if not isinstance(row, dict) or row.get("pr_url") not in allowed:
            continue
        url = str(row["pr_url"])
        prior = merged.get(url)
        if prior is not None and row.get("audit_status") in {"deferred", "unknown"}:
            # A failed/unavailable attempt is not a new observation of the PR.
            # Preserve the last known stage and attach the failed attempt for transparency.
            attempt = {
                "audited_at": row.get("audited_at"),
                "audit_status": row.get("audit_status"),
                "evidence_gaps": row.get("evidence_gaps", []),
            }
            merged[url] = {
                **prior,
                "last_attempt_at": row.get("audited_at"),
                "last_attempt_status": row.get("audit_status"),
                "last_attempt_evidence_gaps": row.get("evidence_gaps", []),
                "last_audit_attempt": attempt,
            }
        else:
            merged[url] = row
    return [merged[url] for url in current_urls if url in merged]


def load_realization_evidence(path: Path) -> dict[str, dict[str, Any]]:
    """Read the append-only, manually attested realization evidence registry."""
    records: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and isinstance(row.get("pr_url"), str):
            records[row["pr_url"]] = row
    return records


def valid_realization_receipt(
    receipt: dict[str, Any] | None, pr_url: str, contributor_login: str | None
) -> bool:
    """Require explicit, independent, linked evidence; never infer realization."""
    if not isinstance(receipt, dict) or receipt.get("pr_url") != pr_url:
        return False
    if receipt.get("status") != "verified" or receipt.get("independence_attested") is not True:
        return False
    verifier = str(receipt.get("verified_by") or "").strip().lower()
    operator = os.environ.get("HELP_WANTED_AUTHOR", "timerloggedout-spec").lower()
    if not verifier or verifier in {operator, "github-actions[bot]", (contributor_login or "").lower()}:
        return False
    if not str(receipt.get("verification_method") or "").strip():
        return False
    if not str(receipt.get("evidence_summary") or "").strip():
        return False
    for field in ("effect_url", "verification_url"):
        parsed = urllib.parse.urlparse(str(receipt.get(field) or ""))
        if parsed.scheme != "https" or not parsed.netloc:
            return False
    try:
        verified_at = datetime.fromisoformat(
            str(receipt.get("verified_at") or "").replace("Z", "+00:00")
        )
        if verified_at.tzinfo is None:
            return False
    except ValueError:
        return False
    return True


def audit_one(
    pr_url: str, realization_evidence: dict[str, Any] | None = None
) -> dict[str, Any]:
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

    files_rows = files if isinstance(files, list) else []
    names = [str(row.get("filename") or "") for row in files_rows]
    files_total_count = int(pr.get("changed_files") or 0)
    files_truncated = isinstance(files, list) and files_total_count > len(files)
    files_complete = isinstance(files, list) and not files_error and not files_truncated
    changed = [
        row for row in files_rows
        if (int(row.get("additions") or 0) + int(row.get("deletions") or 0)) > 0
    ]
    implementation_files = [row for row in changed if row.get("filename") != STAKE_PATH]
    body = str(pr.get("body") or "")
    contributor_login = str((pr.get("user") or {}).get("login") or "")
    proof_present = all(marker in body for marker in SOLUTION_PROOF)
    stake_only = files_complete and bool(changed) and not implementation_files
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
        "audit_status": (
            "partial"
            if files_error or checks_error or checks_truncated or files_truncated
            else "observed"
        ),
        "state": pr.get("state"),
        "merged": bool(pr.get("merged_at")),
        "head_sha": head_sha,
        "contributor_login": contributor_login or None,
        "base_sha": (pr.get("base") or {}).get("sha"),
        "changed_file_count": len(changed),
        "files_total_count": files_total_count,
        "files_observed_count": len(files_rows),
        "files_truncated": files_truncated,
        "files_complete": files_complete,
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
    if files_truncated:
        base["evidence_gaps"].append("files_truncated")
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
    elif files_truncated:
        # The first page cannot establish stake-only or implementation status.
        base["stage"] = "unknown"
    elif stake_only:
        base["stage"] = "stake_only"
    elif implementation_files and proof_present and checks_pass and not files_truncated:
        base["stage"] = "validated_solution"
    elif implementation_files and proof_present:
        base["stage"] = "solution_claimed_unvalidated"
    elif implementation_files:
        base["stage"] = "implementation_unproven"
    else:
        base["stage"] = "unknown"

    # A merge is not, by itself, proof of downstream realized effect.
    realization_valid = valid_realization_receipt(
        realization_evidence, pr_url, contributor_login
    )
    base["realized_effect_verified"] = realization_valid
    if realization_valid:
        base["realization_note"] = "verified through a separately linked, independently attested effect receipt"
        base["realization_evidence"] = {
            "effect_url": realization_evidence["effect_url"],
            "verification_url": realization_evidence["verification_url"],
            "verified_by": realization_evidence["verified_by"],
            "verified_at": realization_evidence["verified_at"],
            "verification_method": realization_evidence["verification_method"],
        }
    else:
        base["realization_note"] = "requires a separately linked, independently verified effect receipt"
        if realization_evidence:
            base["evidence_gaps"].append("realization_receipt_invalid_or_not_independent")
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default="docs/ops/generated/help-wanted-status.json")
    parser.add_argument("--out", default="docs/ops/generated/help-wanted-tribute-audit.json")
    parser.add_argument("--dashboard", default="apps/help-wanted-dashboard/data/status.json")
    parser.add_argument("--max-prs", type=int, default=25)
    parser.add_argument(
        "--realization-evidence",
        default="docs/ops/help-wanted-realization-evidence.jsonl",
        help="append-only JSONL of independently attested realized-effect receipts",
    )
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
    previous_items = []
    previous_path = Path(args.out)
    if previous_path.exists():
        try:
            previous_report = json.loads(previous_path.read_text(encoding="utf-8"))
            previous_items = previous_report.get("items") or []
        except (OSError, json.JSONDecodeError):
            previous_items = []
    realization_by_pr = load_realization_evidence(Path(args.realization_evidence))
    results = [audit_one(url, realization_by_pr.get(url)) for url in selected]
    history_items = merge_audit_history(urls, previous_items, results)
    stages = Counter(row["stage"] for row in history_items)
    statuses = Counter(row.get("last_attempt_status", row.get("audit_status", "observed")) for row in history_items)
    observed_history_count = sum(
        row.get("audit_status", "observed") == "observed"
        for row in history_items
    )
    observed_this_run_count = sum(
        row.get("audit_status", "observed") == "observed"
        for row in results
    )
    deferred_this_run_count = sum(row.get("audit_status") == "deferred" for row in results)
    unknown_this_run_count = sum(row.get("audit_status") == "unknown" for row in results)
    report = {
        "schema_version": "help-wanted.tribute-audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_status_generated_at": board.get("generated_at"),
        "source_tribute_count": len(tributes),
        "unique_pr_count": len(urls),
        "audited_pr_count": observed_history_count,
        "audited_this_run_count": observed_this_run_count,
        "attempted_this_run_count": len(results),
        "deferred_this_run_count": deferred_this_run_count,
        "unknown_this_run_count": unknown_this_run_count,
        "audited_this_run_pr_urls": [
            row["pr_url"] for row in results
            if row.get("audit_status", "observed") not in {"deferred", "unknown"}
        ],
        "not_audited_count": max(0, len(urls) - observed_history_count),
        "audit_window_start": start,
        "audit_window_size": batch_size,
        "stages": dict(stages),
        "audit_statuses": dict(statuses),
        "realized_effect_verified_count": sum(bool(row.get("realized_effect_verified")) for row in history_items),
        "policy": {
            "claim_is_solution": False,
            "merge_is_realized_effect": False,
            "missing_evidence_is_success": False,
            "audit_is_read_only": True,
        },
        "items": history_items,
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
        "audited": observed_history_count,
        "audited_this_run": observed_this_run_count,
        "attempted_this_run": len(results),
        "not_audited": max(0, len(urls) - observed_history_count),
        "unique_prs": len(urls),
        "stages": dict(stages),
        "realized_effect_verified": report["realized_effect_verified_count"],
        "output": str(out_path),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
