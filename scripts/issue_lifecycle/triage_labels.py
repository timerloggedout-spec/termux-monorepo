#!/usr/bin/env python3
"""Deterministic label application for unlabelled open issues.

The issue-lifecycle map (docs/ops/ISSUE-LIFECYCLE.md, G1/G2) records that
the LLM triage chain (gemini-dispatch -> gemini-triage) posts advisory
comments but never applies labels, and that its provider route is
fragile (HTTP 429 "incomplete" comments; some issues get no comment).
This script is the provider-independent floor: it labels ONLY issues
that currently have no labels at all, ONLY from title-prefix rules that
map to labels which already exist in the repo taxonomy, and it never
removes or changes an existing label.

Usage (offline / tests):
    propose_labels(title, existing_labels) -> list[str]

Usage (Actions / lane pass):
    python3 scripts/issue_lifecycle/triage_labels.py --report
    python3 scripts/issue_lifecycle/triage_labels.py --apply

API access uses GITHUB_TOKEN (Actions) or GH_TOKEN from the
environment and the stdlib only; the repo defaults to
timerloggedout-spec/termux-monorepo and can be overridden with
GITHUB_REPOSITORY.
"""

import argparse
import json
import os
import sys
import urllib.request

API = "https://api.github.com"
DEFAULT_REPO = "timerloggedout-spec/termux-monorepo"

# Labels this pass may apply. Every entry must already exist in the
# repo label taxonomy (docs/ops/ISSUE-LIFECYCLE.md section 2); the
# point of the pass is applying the taxonomy, never inventing it.
KNOWN_LABELS = {"proposal", "research", "target-brief", "delphi:rfp", "bug"}


def propose_labels(title, existing_labels):
    """Return the deterministic labels for one issue.

    Conservative by construction: an issue that already has any label
    is out of scope ([]), and a title that matches no rule gets [].
    """
    if existing_labels:
        return []
    t = (title or "").strip()
    low = t.lower()
    labels = []
    if low.startswith("[target]") or low.startswith("[target "):
        labels = ["target-brief"]
    elif low.startswith("[delphi:rfp]") or low.startswith("delphi:rfp"):
        labels = ["delphi:rfp"]
    elif low.startswith("proposal:") or low.startswith("[proposal]"):
        labels = ["proposal"]
        if "investigate" in low:
            labels.append("research")
    elif low.startswith("bug:") or low.startswith("[bug]"):
        labels = ["bug"]
    return [label for label in labels if label in KNOWN_LABELS]


def _request(method, path, token, repo, body=None):
    url = f"{API}/repos/{repo}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def list_open_items(repo, token):
    items, page = [], 1
    while True:
        batch = _request(
            "GET",
            f"/issues?state=open&sort=created&direction=desc&per_page=100&page={page}",
            token,
            repo,
        )
        if not isinstance(batch, list):
            return items
        items.extend(batch)
        if len(batch) < 100:
            return items
        page += 1


def run(mode, repo, token, out=sys.stdout):
    items = list_open_items(repo, token)
    issues = [i for i in items if "pull_request" not in i]
    unlabelled = [i for i in issues if not i.get("labels")]
    print(
        f"open issues: {len(issues)}; unlabelled: {len(unlabelled)}",
        file=out,
    )
    applied = 0
    for issue in unlabelled:
        labels = propose_labels(
            issue.get("title", ""),
            [label.get("name") for label in issue.get("labels", [])],
        )
        if not labels:
            print(f"#{issue['number']}: no rule matches - lane pass decides", file=out)
            continue
        if mode == "apply":
            _request(
                "POST",
                f"/issues/{issue['number']}/labels",
                token,
                repo,
                {"labels": labels},
            )
            applied += 1
            print(f"#{issue['number']}: applied {labels}", file=out)
        else:
            print(f"#{issue['number']}: would apply {labels}", file=out)
    print(f"mode={mode}; labelled this run: {applied if mode == 'apply' else 0}", file=out)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="list proposals only")
    group.add_argument("--apply", action="store_true", help="apply proposed labels")
    args = parser.parse_args(argv)
    repo = os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    return run("apply" if args.apply else "report", repo, token)


if __name__ == "__main__":
    sys.exit(main())
