#!/usr/bin/env python3
"""QUE #4977 Fix 3b — scheduled re-evaluation of deferred-by-tier filings.

Admission-only machinery. It never opens/reopens issues, invokes a provider,
starts build-dispatch, changes governor thresholds, or claims work. It scans
existing open deferred filings, reuses swarm_admission's canonical matcher,
evaluator and picture freshness rules, and changes only admission labels plus
an idempotent receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE / "scripts" / "ops"))
import swarm_admission as admission  # noqa: E402

REPO = os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")
API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
MARK_RE = re.compile(r"<!-- que-admission-drain:v1 sha256=([0-9a-f]{64}) -->")
PAGE_SIZE = 100


class GitHub:
    def __init__(self, token: str):
        if not token:
            raise RuntimeError("missing GitHub token")
        self.token = token

    def request(self, method: str, path: str, body=None):
        url = path if path.startswith("http") else API + path
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "que-admission-drain",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        if data is not None:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=40) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}

    def get(self, path):
        return self.request("GET", path)

    def post(self, path, body):
        return self.request("POST", path, body)

    def delete(self, path):
        return self.request("DELETE", path)


def pages(gh: GitHub, path: str):
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        rows = gh.get(f"{path}{sep}per_page={PAGE_SIZE}&page={page}")
        if not isinstance(rows, list):
            raise RuntimeError(f"GitHub collection had unexpected shape at page {page}")
        yield from rows
        if len(rows) < PAGE_SIZE:
            break
        page += 1


def collect_live_picture(gh: GitHub, now: datetime):
    runs = []
    for status in ("queued", "in_progress"):
        page = 1
        while True:
            query = urllib.parse.urlencode({
                "status": status, "per_page": 50, "page": page
            })
            try:
                payload = gh.get(f"/repos/{REPO}/actions/runs?{query}")
                batch = payload.get("workflow_runs")
                if not isinstance(batch, list):
                    raise RuntimeError("malformed_body")
            except Exception as exc:
                code = getattr(exc, "code", None)
                message = str(exc).lower()
                if "rate limit" in message:
                    error_class = "rate_limited"
                elif code:
                    error_class = f"http_{code}"
                else:
                    error_class = type(exc).__name__
                return {"collection_error": {
                    "failed_status": status, "failed_page": page,
                    "error_class": error_class,
                }}
            runs.extend({
                "name": row.get("name"),
                "status": row.get("status"),
                "created_at": row.get("created_at", ""),
            } for row in batch)
            if len(batch) < 50:
                break
            page += 1
    return {
        "picture_source": "live-fallback",
        "collected_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runs": runs,
    }


def resolve_picture(gh: GitHub, feeds_dir: str, now: datetime):
    fresh = admission.picture_from_feeds(feeds_dir, now)
    if fresh is not None:
        runs, meta = fresh
        return {"status": "ok", "runs": runs, **meta}
    fallback = collect_live_picture(gh, now)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
        json.dump(fallback, fh)
        path = fh.name
    try:
        return admission.resolve_picture(
            feeds_dir, path, now, admission.FEED_FRESH_SECONDS
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def registry_from_templates(directory: str):
    registry = {}
    for path in sorted(Path(directory).glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        block = admission.parse_block(text)
        if block:
            labels, prefix = admission.template_identity(text)
            registry[path.name] = (block, labels, prefix)
    return registry


def decide(block, tiers_doc, picture, now):
    """Mirror swarm_admission.main's fail-soft/non-flow-tier semantics."""
    try:
        if picture.get("status") == "ok":
            decision, reasons, facts = admission.evaluate(
                block, tiers_doc, picture["runs"], now=now
            )
            facts["picture"] = {
                "source": picture.get("source"),
                "as_of": picture.get("as_of"),
            }
        elif block["que_tier"] in admission.NON_FLOW_TIERS:
            decision, reasons, facts = admission.evaluate(
                block, tiers_doc, [], now=now
            )
            facts["picture"] = {
                "source": "unavailable",
                "detail": picture.get("detail", "queue picture unavailable"),
                "tolerated": True,
            }
        else:
            decision = "DEFERRED"
            reasons = [f"queue picture unavailable: {picture.get('detail', 'cause unknown')}"]
            facts = {
                "tier": block["que_tier"], "queued_depth": -1,
                "after": {}, "chain": {},
                "picture": {
                    "source": "unavailable",
                    "detail": picture.get("detail", "queue picture unavailable"),
                },
            }
    except Exception as exc:
        decision = "DEFERRED"
        reasons = [f"admission evaluation error: {type(exc).__name__}: {exc}"]
        facts = {"tier": block["que_tier"], "queued_depth": -1,
                 "after": {}, "chain": {}}
    return decision, reasons, facts


def fingerprint(decision, reasons, facts) -> str:
    # Keep source provenance in the receipt, but exclude the moving
    # collector timestamp from identity. Otherwise unchanged decisions
    # emit a new issue comment every 15-minute drain cycle.
    stable_facts = dict(facts)
    picture = stable_facts.get("picture")
    if isinstance(picture, dict):
        picture = dict(picture)
        picture.pop("as_of", None)
        stable_facts["picture"] = picture
    payload = json.dumps(
        {"decision": decision, "reasons": reasons, "facts": stable_facts},
        sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def admission_label_delta(current_labels, decision):
    """Return only admission-label changes; preserve dispatch/claim labels."""
    current = set(current_labels)
    if decision == "ADMITTED":
        return (["deferred-by-tier"] if "deferred-by-tier" in current else [],
                ["swarm-admitted"] if "swarm-admitted" not in current else [])
    return (["swarm-admitted"] if "swarm-admitted" in current else [],
            ["deferred-by-tier"] if "deferred-by-tier" not in current else [])


def latest_fingerprint(comments):
    for comment in reversed(comments):
        match = MARK_RE.search(comment.get("body") or "")
        if match:
            return match.group(1)
    return None


def receipt_body(fname, block, decision, reasons, facts, run_url, digest):
    body = admission.stamp(fname, block, decision, reasons, facts, run_url)
    return body + f"\n\n<!-- que-admission-drain:v1 sha256={digest} -->"


def process(gh, issue, registry, tiers_doc, picture, now, run_url, dry_run=False):
    labels = {
        label.get("name") for label in issue.get("labels", [])
        if isinstance(label, dict)
    }
    if "deferred-by-tier" not in labels or issue.get("pull_request"):
        return {"issue": issue.get("number"), "action": "skip_not_deferred"}
    fname, block = admission.match_template(
        registry, labels, issue.get("title") or ""
    )
    if not block:
        return {"issue": issue["number"], "action": "skip_unmatched"}
    comments = list(pages(
        gh, f"/repos/{REPO}/issues/{issue['number']}/comments"
    ))
    if "dispatch-claimed" in labels or any(
        "PRODUCER CLAIM" in (comment.get("body") or "")
        for comment in comments
    ):
        return {"issue": issue["number"], "action": "skip_already_claimed"}
    decision, reasons, facts = decide(block, tiers_doc, picture, now)
    digest = fingerprint(decision, reasons, facts)
    remove, add = admission_label_delta(labels, decision)
    same_receipt = latest_fingerprint(comments) == digest
    run_url = run_url or f"https://github.com/{REPO}/actions"
    body = receipt_body(fname, block, decision, reasons, facts, run_url, digest)
    changed = bool(remove or add or not same_receipt)
    result = {
        "issue": issue["number"], "template": fname,
        "decision": decision, "action": "would_update" if changed else "unchanged",
        "reasons": reasons, "picture": facts.get("picture"),
    }
    if dry_run or not changed:
        return result

    # Re-read immediately before mutation. A concurrent producer claim or
    # human state change wins; admission must never overwrite a claimed task.
    fresh_issue = gh.get(f"/repos/{REPO}/issues/{issue['number']}")
    fresh_labels = {
        label.get("name") for label in fresh_issue.get("labels", [])
        if isinstance(label, dict)
    }
    fresh_comments = list(pages(
        gh, f"/repos/{REPO}/issues/{issue['number']}/comments"
    ))
    if fresh_issue.get("state") != "open" or "deferred-by-tier" not in fresh_labels:
        return {"issue": issue["number"], "action": "skip_state_changed"}
    if "dispatch-claimed" in fresh_labels or any(
        "PRODUCER CLAIM" in (comment.get("body") or "")
        for comment in fresh_comments
    ):
        return {"issue": issue["number"], "action": "skip_already_claimed"}

    # Recompute the label delta and receipt idempotency from the fresh read.
    remove, add = admission_label_delta(fresh_labels, decision)
    same_receipt = latest_fingerprint(fresh_comments) == digest

    # Apply the new admission label before removing the deferred label. If
    # either API call fails, the next scheduled pass can safely reconcile.
    if add:
        gh.post(f"/repos/{REPO}/issues/{issue['number']}/labels", {"labels": add})
    for label in remove:
        try:
            gh.delete(f"/repos/{REPO}/issues/{issue['number']}/labels/{urllib.parse.quote(label, safe='')}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
    if not same_receipt:
        gh.post(f"/repos/{REPO}/issues/{issue['number']}/comments", {"body": body})
    result["action"] = "updated"
    return result


def main(argv=None):
    global REPO
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--templates-dir", default=".github/ISSUE_TEMPLATE")
    parser.add_argument("--tiers", default="ops/quota/dispatch-tiers.json")
    parser.add_argument("--feeds-dir", default="ops/que/feeds")
    parser.add_argument("--max-issues", type=int, default=100)
    parser.add_argument("--now", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    REPO = args.repo
    now = admission._parse_ts(args.now) if args.now else datetime.now(timezone.utc)
    gh = GitHub(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "")
    registry = registry_from_templates(args.templates_dir)
    tiers_doc = json.loads(Path(args.tiers).read_text(encoding="utf-8"))
    picture = resolve_picture(gh, args.feeds_dir, now)
    issues = list(pages(
        gh, f"/repos/{REPO}/issues?state=open&labels=deferred-by-tier"
    ))
    issues = [item for item in issues if not item.get("pull_request")][:args.max_issues]
    results = [
        process(gh, issue, registry, tiers_doc, picture, now,
                args.run_url, args.dry_run)
        for issue in issues
    ]
    summary = {
        "schema": "que-admission-drain/v1",
        "generated_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "picture": {k: picture.get(k) for k in ("status", "source", "as_of", "detail")},
        "scanned": len(issues),
        "admitted": sum(r.get("decision") == "ADMITTED" for r in results),
        "deferred": sum(r.get("decision") == "DEFERRED" for r in results),
        "updated": sum(r.get("action") == "updated" for r in results),
        "dry_run": args.dry_run,
        "results": results,
    }
    output = json.dumps(summary, indent=2, sort_keys=True)
    print(output)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write("## QUE deferred-admission drain\n\n")
            fh.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
