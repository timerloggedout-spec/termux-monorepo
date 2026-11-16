#!/usr/bin/env python3
"""Build a conservative, machine-readable Git branch reconciliation inventory.

Requires: git, gh (authenticated), Python 3.10+.
Read-only with respect to GitHub: never merges, pushes, closes, or deletes branches.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(args: list[str], *, check: bool = True, cwd: str | Path | None = None) -> str:
    proc = subprocess.run(args, text=True, capture_output=True, cwd=cwd)
    if check and proc.returncode:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def gh_pages(endpoint: str) -> list[dict[str, Any]]:
    raw = run(["gh", "api", "--paginate", "--slurp", endpoint])
    pages = json.loads(raw or "[]")
    if not isinstance(pages, list):
        raise RuntimeError(f"unexpected GitHub API pagination payload for {endpoint}")
    return [row for page in pages if isinstance(page, list) for row in page if isinstance(row, dict)]


def git_count(base: str, head: str, *, cwd: str | Path | None = None) -> tuple[int, int] | None:
    # `git cat-file -e` succeeds with empty stdout; inspect its exit code.
    for ref in (base, head):
        probe = subprocess.run(["git", "cat-file", "-e", f"{ref}^{{commit}}"], text=True, capture_output=True, cwd=cwd)
        if probe.returncode != 0:
            return None
    merge_base = run(["git", "merge-base", base, head], check=False, cwd=cwd)
    if not merge_base:
        return None
    counts = run(["git", "rev-list", "--left-right", "--count", f"{base}...{head}"], cwd=cwd)
    behind, ahead = (int(x) for x in counts.split())
    return ahead, behind


def classify(ahead: int, behind: int) -> str:
    if ahead == 0 and behind == 0:
        return "identical"
    if ahead == 0:
        return "behind-only"
    if behind == 0:
        return "ahead-only"
    return "diverged"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repository")
    parser.add_argument("--default-branch", required=True)
    parser.add_argument("--output-dir", default="artifacts/branch-reconciliation")
    args = parser.parse_args()

    owner, repo = args.repo.split("/", 1)
    run(["git", "fetch", "--no-tags", "origin", "+refs/heads/*:refs/remotes/origin/*"])
    branches = gh_pages(f"repos/{args.repo}/branches?per_page=100")
    pulls = gh_pages(f"repos/{args.repo}/pulls?state=all&per_page=100")
    default_ref = f"refs/remotes/origin/{args.default_branch}"
    if run(["git", "rev-parse", "--verify", default_ref], check=False) == "":
        raise RuntimeError(f"default branch ref unavailable locally: {default_ref}")

    prs_by_head: dict[str, list[dict[str, Any]]] = {}
    for pr in pulls:
        head = pr.get("head") or {}
        ref = head.get("ref")
        head_repo = (head.get("repo") or {}).get("full_name")
        if ref and head_repo == args.repo:
            prs_by_head.setdefault(ref, []).append(pr)

    records: list[dict[str, Any]] = []
    for branch in branches:
        name = branch.get("name")
        commit = (branch.get("commit") or {}).get("sha")
        if not name or not commit:
            continue
        local_ref = f"refs/remotes/origin/{name}"
        # API SHA is authoritative; a missing local ref is explicitly unresolved.
        local_sha = run(["git", "rev-parse", "--verify", f"{local_ref}^{{commit}}"], check=False)
        comparison = git_count(default_ref, local_ref) if local_sha else None
        linked_prs = prs_by_head.get(name, [])
        pr_summaries = [{
            "number": p.get("number"),
            "state": p.get("state"),
            "merged_at": p.get("merged_at"),
            "draft": p.get("draft"),
            "base_ref": (p.get("base") or {}).get("ref"),
            "base_sha": (p.get("base") or {}).get("sha"),
            "head_sha": (p.get("head") or {}).get("sha"),
            "head_repo": ((p.get("head") or {}).get("repo") or {}).get("full_name"),
            "url": p.get("html_url"),
        } for p in linked_prs]
        if not local_sha or local_sha != commit:
            disposition, ahead, behind = "unresolved-local-ref", None, None
        elif comparison is None:
            disposition, ahead, behind = "unrelated-or-unavailable-history", None, None
        else:
            ahead, behind = comparison
            disposition = classify(ahead, behind)
        records.append({
            "branch": name,
            "sha": commit,
            "protected": branch.get("protected"),
            "local_ref_sha": local_sha or None,
            "default_branch": args.default_branch,
            "ahead_of_default": ahead,
            "behind_default": behind,
            "disposition": disposition,
            "pull_requests": pr_summaries,
            "promotion_review_required": True,
            "automatic_promotion": False,
        })

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    report = {
        "schema": "branch-reconciliation-registry/v1",
        "repository": args.repo,
        "default_branch": args.default_branch,
        "generated_at": now,
        "inventory_complete_for_api_pages": True,
        "branch_count": len(records),
        "pull_request_count": len(pulls),
        "policy": {
            "read_only": True,
            "never_auto_merge": True,
            "never_auto_delete": True,
            "missing_evidence_means_unresolved": True,
            "promotion_requires_human_review": True,
            "branch_api_is_authoritative_for_branch_presence": True,
        },
        "branches": records,
    }

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "inventory.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# Branch reconciliation: {args.repo}", "",
        f"- Generated: {now}",
        f"- Default branch: `{args.default_branch}`",
        f"- Branches inventoried: **{len(records)}**",
        f"- Pull requests inspected: **{len(pulls)}**",
        "- Mode: read-only; no merge, close, push, or delete actions", "",
        "| Branch | Ahead | Behind | Disposition | Open/closed PRs |",
        "|---|---:|---:|---|---:|",
    ]
    for row in sorted(records, key=lambda x: x["branch"].casefold()):
        a = row["ahead_of_default"] if row["ahead_of_default"] is not None else "?"
        b = row["behind_default"] if row["behind_default"] is not None else "?"
        lines.append(f"| `{row['branch']}` | {a} | {b} | {row['disposition']} | {len(row['pull_requests'])} |")
    lines += ["", "## Interpretation", "",
        "- `ahead-only`: unique commits exist relative to the default branch; review for promotion.",
        "- `diverged`: both sides contain unique commits; reconcile against the intended PR base before promotion.",
        "- `behind-only` / `identical`: no unique branch commits relative to the default branch; do not infer that the branch is safe to delete.",
        "- `unresolved-*`: evidence is incomplete; do not promote or discard.",
        "- PRs targeting non-default bases still require a separate base-relative review.",
        "", "This report is an inventory and triage aid, not a merge authorization.", ""]
    (out / "inventory.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}/inventory.json and {out}/inventory.md ({len(records)} branches)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"branch reconciliation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
