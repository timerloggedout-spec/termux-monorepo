#!/usr/bin/env python3
"""Collect research issue filings into an observatory-intake/v1 document.

The Observatory's fourth signal source (after owned/starred/watched):
issues filed through the research issue templates (labels
research:provider / research:service, PR #2058) or carrying the umbrella
research label with a parseable form body. Parsing is delegated to
scripts/research/research_intake.py — the same parser the research-intake
workflow comments back with — so the issue record and the Observatory
record can never drift. A filing is a research signal, never an adoption
order. Unparseable filings are counted and skipped, never fatal.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.github.repository_observatory import get_json  # noqa: E402
from scripts.research import research_intake as ri  # noqa: E402

LABELS = ("research:provider", "research:service")


def entry_from_issue(issue: dict[str, Any]) -> dict[str, Any] | None:
    labels = {l.get("name") for l in issue.get("labels") or [] if isinstance(l, dict)}
    kind = ("provider" if "research:provider" in labels else
            "service" if "research:service" in labels else None)
    if kind is None:
        return None
    body = issue.get("body") or ""
    fields = ri.parse_command(body) if "<!-- request-research -->" in body else ri.parse_form(body)
    rec = ri.build_record(kind, fields)  # raises ValueError on a bad filing
    return {
        "issue": issue.get("number"),
        "kind": kind,
        "seed_id": rec["seed_id"],
        "name": rec["observed_facts"]["name"],
        "upstream": (fields.get("upstream") or "").strip(),
        "url": rec["observed_facts"]["url"],
        "signal": rec["starter"]["signal"],
        "category": rec["classification"]["domains"][0],
        "filed_at": issue.get("created_at"),
    }


def collect(issues: list[dict[str, Any]]) -> dict[str, Any]:
    entries, skipped, seen = [], 0, set()
    for issue in issues:
        if issue.get("pull_request") or issue.get("number") in seen:
            continue
        seen.add(issue.get("number"))
        try:
            e = entry_from_issue(issue)
        except ValueError:
            skipped += 1
            continue
        if e is None:
            continue
        entries.append(e)
    entries.sort(key=lambda e: e["issue"] or 0)
    return {"schema_version": "observatory-intake/v1",
            "generated_from": "issues labeled research:provider/research:service",
            "skipped_unparseable": skipped, "entries": entries}


def main(argv: list[str] | None = None, fetch: Callable[..., Any] = get_json) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--token-env", default="REPOSITORY_OBSERVATORY_TOKEN")
    args = ap.parse_args(argv)
    import os
    token = os.environ.get(args.token_env) or os.environ.get("GITHUB_TOKEN")
    if not token:
        print(f"missing {args.token_env} or GITHUB_TOKEN", file=sys.stderr)
        return 2
    issues: list[dict[str, Any]] = []
    for label in LABELS:
        page = 1
        while True:
            batch = fetch(f"/repos/{args.repo}/issues", token,
                          {"labels": label, "state": "all", "per_page": 100, "page": page})
            if not isinstance(batch, list):
                raise RuntimeError("expected list from issues")
            issues.extend(x for x in batch if isinstance(x, dict))
            if len(batch) < 100:
                break
            page += 1
    doc = collect(issues)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"entries": len(doc["entries"]),
                      "skipped_unparseable": doc["skipped_unparseable"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
