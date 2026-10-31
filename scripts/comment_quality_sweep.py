#!/usr/bin/env python3
"""Comment-quality sweep for fleet record surfaces.

Standard: docs/ops/COMMENT-QUALITY.md. Record surfaces are the issues
pinned in ops/delphi/ledgers.json (continuous ledgers + living records,
incl. the results board) plus the Delphi queue issues carrying the
labels delphi:rfp or delphi:participant.

Classification is deliberately conservative — a comment is deletable
noise ONLY when it matches an exact, verified spam class:

  vendor-promo        author blocksorg[bot] AND body starts with the
                      Blocks onboarding pitch ("Mention Blocks like a
                      regular teammate"). One identical drop is posted
                      on every new issue by the Blocks GitHub App.
  automation-failure  a peer-router triage/review marker comment
                      (<!-- <provider>-<role> -->) whose body carries
                      "invocation incomplete" — a failed-call stub with
                      no classification, evidence or decision. The one
                      completed triage in the 2026-10-28 census carried
                      a real classification and is NOT in this class.

Everything else is productive by default and is NEVER deleted by this
sweep: ledger marker events (<!-- delphi-* -->), signed coordination
appendices ([MUSEai]@{role:{...}}), completed automation output, and
human/operator evidence, decisions and corrections. This matches the
ledger-feed noise definition (scripts/delphi/ledger_feed.py): on a
ledger issue a comment is an event iff it starts with a ledger marker
or '[MUSEai]@'; the sweep only ever removes the two classes above,
which are noise under every surface's rule.

Usage:
  GH_TOKEN=... comment_quality_sweep.py [--repo owner/repo] [--delete]
Without --delete the sweep is report-only and prints counts per surface
and per class. With --delete it deletes exactly the two noise classes
and re-counts. Exit code is 0 on a completed sweep; noise found in
report mode is data, not a failure.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

API = "https://api.github.com"
VENDOR_AUTHOR = "blocksorg[bot]"
VENDOR_PREFIX = "Mention Blocks like a regular teammate"
FAILURE_MARKER = re.compile(r"^<!-- (openrouter|omni|felo|huggingface)-[a-z]+ -->")
FAILURE_TEXT = "invocation incomplete"
QUEUE_LABELS = ("delphi:rfp", "delphi:participant")


def classify(comment: dict) -> str:
    """Return the comment's class. Only two classes are deletable."""
    body = comment.get("body") or ""
    author = (comment.get("user") or {}).get("login") or ""
    if author == VENDOR_AUTHOR and body.startswith(VENDOR_PREFIX):
        return "vendor-promo"
    if body.startswith("<!--"):
        if FAILURE_TEXT in body and FAILURE_MARKER.match(body):
            return "automation-failure"
        if body.startswith("<!-- delphi") or body.startswith("<!-- delphi-board"):
            return "ledger-event"
    elif body.startswith("[MUSEai]@"):
        return "signed-append"
    return "substantive-other"


DELETABLE = ("vendor-promo", "automation-failure")


def record_surfaces(repo: str, registry_path: str, get) -> list[int]:
    """Registry-pinned issues + the Delphi queue, de-duplicated."""
    issues: set[int] = set()
    with open(registry_path, encoding="utf-8") as stream:
        registry = json.load(stream)
    for entry in registry.get("ledgers", []) + registry.get("living_records", []):
        if isinstance(entry.get("issue"), int):
            issues.add(entry["issue"])
    for label in QUEUE_LABELS:
        for issue in get(f"/repos/{repo}/issues?labels={label}&state=all"):
            if "pull_request" not in issue:
                issues.add(issue["number"])
    return sorted(issues)


def make_client(token: str):
    def call(method: str, path: str):
        req = urllib.request.Request(API + path, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {"status": resp.status}

    def get(path: str):
        out, page = [], 1
        while True:
            sep = "&" if "?" in path else "?"
            batch = call("GET", f"{path}{sep}per_page=100&page={page}")
            if not isinstance(batch, list):
                return batch
            out.extend(batch)
            if len(batch) < 100:
                return out
            page += 1

    return call, get


def sweep(repo: str, registry_path: str, delete: bool, call, get) -> dict:
    totals: dict[str, int] = {}
    deleted = 0
    per_issue = {}
    for number in record_surfaces(repo, registry_path, get):
        counts: dict[str, int] = {}
        for comment in get(f"/repos/{repo}/issues/{number}/comments"):
            cls = classify(comment)
            counts[cls] = counts.get(cls, 0) + 1
            totals[cls] = totals.get(cls, 0) + 1
            if delete and cls in DELETABLE:
                call("DELETE", f"/repos/{repo}/issues/comments/{comment['id']}")
                deleted += 1
        if counts:
            per_issue[number] = counts
    return {"issues": per_issue, "totals": totals, "deleted": deleted}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--registry", default="ops/delphi/ledgers.json")
    ap.add_argument("--delete", action="store_true",
                    help="delete the two verified noise classes (default: report only)")
    args = ap.parse_args()
    if not args.repo:
        print("error: --repo or GITHUB_REPOSITORY required", file=sys.stderr)
        return 2
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    call, get = make_client(token)
    result = sweep(args.repo, args.registry, args.delete, call, get)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
