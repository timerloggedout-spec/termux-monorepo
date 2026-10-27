#!/usr/bin/env python3
"""Reviewer performance metrics collector (reviewer-metrics/v1).

Aggregates the peer-review orchestrator's SHA-bound state comments plus the
reviews / comments APIs into a provider x context x metric map:

    docs/ops/generated/reviewer-metrics.json

The map is the measurement layer of the reviewer JIT system
(docs/ops/REVIEWER-JIT-DESIGN.md): the orchestrator records context and
adaptations per cycle, this collector aggregates them, and the JIT policy
rules consume the aggregates. Every figure is derived from live API data at
collection time; nothing is copied forward from earlier snapshots.

Stdlib only. Auth: GH_TOKEN or GITHUB_TOKEN env (in Actions, the operator
token secrets). Usage:

    collect.py --repo owner/name --limit 60 --out reviewer-metrics.json
"""
import argparse
import json
import os
import re
import statistics
import sys
import urllib.request
from datetime import datetime, timezone

STATE_MARKER = "<!-- agent-peer-response-state:v2 -->"

# Mirror of the orchestrator's provider login map (peer-review-orchestrator.yml),
# plus ECC Tools, which participates as a comment-only reviewer (mirrored to
# check runs by agent-ecc-tools-ops) but is not an orchestrator provider.
PROVIDER_LOGINS = {
    "coderabbitai[bot]": "coderabbit",
    "qodo-code-review[bot]": "qodo",
    "devin-ai-integration[bot]": "devin",
    "aikido-security[bot]": "aikido",
    "sentry-io[bot]": "sentry",
    "copilot-pull-request-reviewer[bot]": "copilot",
    "ecc-tools[bot]": "ecc",
}

PROVIDER_STATES = {
    "provider_completed",
    "provider_cooldown",
    "awaiting_provider_response",
    "pending_operator_action",
    "action_acknowledged",
    "not_required_bot_authored_pr",
    "not_required_docs_only_context",
    "not_required_zero_delivery_in_context",
}

FIELD_RE = re.compile(r"^([a-z_]+):\s*(.+?)\s*$")
PROVIDER_LINE_RE = re.compile(r"^- ([a-z0-9_-]+): ([a-z_]+)(;.*)?$")

# ECC Tools pr-audit comments (real format, verified on PR #1441):
#   <!-- ecc-tools:pr-audit:<Gate Name>:<40-hex commit sha> -->
#   ## ECC Tools / <Gate Name>
#   **<summary>** (<conclusion>)   conclusion in the check-run vocabulary
ECC_AUDIT_MARKER_RE = re.compile(r"<!--\s*ecc-tools:pr-audit:(.+?):([0-9a-f]{40})\s*-->")
ECC_VERDICT_RE = re.compile(r"\*\*([^*]+)\*\*\s*\(([a-z_]+)\)")


def parse_ecc_audits(comments):
    """Pure: ECC Tools audit comments -> audit records with conclusions."""
    audits = []
    for c in comments:
        if provider_for(c.get("user", {}).get("login")) != "ecc":
            continue
        body = c.get("body") or ""
        m = ECC_AUDIT_MARKER_RE.search(body)
        if not m:
            continue
        v = ECC_VERDICT_RE.search(body)
        audits.append({
            "gate": m.group(1).strip(),
            "commit": m.group(2),
            "conclusion": v.group(2) if v else "",
            "summary": v.group(1).strip() if v else "",
            "created_at": c.get("created_at"),
        })
    return audits


def provider_for(login):
    return PROVIDER_LOGINS.get((login or "").lower(), "")


def author_class(user):
    login = (user or {}).get("login", "") or ""
    if (user or {}).get("type") == "Bot" or login.lower().endswith("[bot]"):
        return "bot"
    return "user"


def classify_file(path):
    """Change-class of one path. MUST stay in sync with the orchestrator's
    JS classifyFilePath (peer-review-orchestrator.yml) and the design doc."""
    base = path.rsplit("/", 1)[-1]
    if path.startswith("docs/ops/generated/") or "/generated/" in path:
        return "generated"
    if path.startswith(".github/workflows/"):
        return "workflows"
    if path.startswith("docs/") or base.endswith((".md", ".rst")):
        return "docs"
    if (
        path.startswith("tests/")
        or "/tests/" in path
        or base.startswith("test_")
        or base.endswith("_test.py")
        or base.endswith((".test.js", ".spec.js"))
    ):
        return "tests"
    ext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    if ext in ("toml", "yaml", "yml"):
        return "config"
    if ext in ("py", "js", "ts", "tsx", "jsx", "go", "rs", "sh", "bash", "c", "h", "cpp", "java", "rb"):
        return "code"
    if ext in ("json", "jsonl", "csv"):
        return "data"
    return "other"


def classify_files(paths):
    counts = {}
    for p in paths:
        counts[classify_file(p)] = counts.get(classify_file(p), 0) + 1
    total = sum(counts.values())
    if not total:
        return {"classes": {}, "primary": "unknown", "docs_only": False, "generated_only": False}
    top_class, top_count = max(counts.items(), key=lambda kv: kv[1])
    # Primary = the sole class, or the class holding a strict majority of
    # files; anything else is "mixed". (Same rule as the orchestrator JS.)
    primary = top_class if (len(counts) == 1 or top_count * 2 > total) else "mixed"
    docs_only = all(c in ("docs", "generated") for c in counts) and "docs" in counts
    generated_only = set(counts) == {"generated"}
    return {"classes": counts, "primary": primary, "docs_only": docs_only, "generated_only": generated_only}


def parse_state_comment(body):
    """Parse one orchestrator state comment; returns None if not one."""
    if not body or STATE_MARKER not in body:
        return None
    fields = {}
    providers = {}
    for line in body.split("\n"):
        m = PROVIDER_LINE_RE.match(line.strip())
        if m and m.group(2) in PROVIDER_STATES:
            providers[m.group(1)] = {"state": m.group(2), "line": line.strip()}
            continue
        f = FIELD_RE.match(line.strip())
        if f and f.group(1) in (
            "cycle_id", "head_sha", "cycle_started_at", "state", "ready",
            "required_providers", "enforce_provider_completion",
            "context_author", "context_author_class", "context_primary_class",
            "context_size", "context_labels", "metrics_map",
        ):
            fields[f.group(1)] = f.group(2)
    if "cycle_id" not in fields:
        return None
    required = [p.strip() for p in (fields.get("required_providers") or "").split(",") if p.strip() and p.strip() != "none"]
    return {"fields": fields, "providers": providers, "required": required}


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_cycle_records(pr, comments, reviews, review_comments, file_paths):
    """Pure: fetched API objects -> per-cycle records for one PR."""
    a_class = author_class(pr.get("user"))
    ctx = classify_files(file_paths or [])
    if ctx["primary"] == "unknown":
        ctx = {
            "classes": {}, "primary": "unknown",
            "docs_only": False, "generated_only": False,
        }
    labels = sorted(l["name"] for l in pr.get("labels", []) if isinstance(l, dict))
    coderabbit_skipped = any(
        provider_for(c.get("user", {}).get("login")) == "coderabbit"
        and "review skipped" in (c.get("body") or "").lower()
        for c in comments
    )
    # Issue-comment volume per provider on this PR.
    volume = {}
    for c in comments:
        p = provider_for(c.get("user", {}).get("login"))
        if p:
            volume[p] = volume.get(p, 0) + 1
    records = []
    for c in comments:
        parsed = parse_state_comment(c.get("body") or "")
        if not parsed:
            continue
        f = parsed["fields"]
        started = parse_ts(f.get("cycle_started_at"))
        head_sha = f.get("head_sha", "")
        # Prefer context recorded in the state comment (P1 cycles); fall back
        # to the collector-derived context for pre-P1 cycles.
        rec_ctx_primary = f.get("context_primary_class") or ctx["primary"]
        provider_recs = {}
        for name, info in parsed["providers"].items():
            latency = None
            evidence_times = []
            for r in reviews:
                if provider_for(r.get("user", {}).get("login")) == name and r.get("commit_id") == head_sha:
                    t = parse_ts(r.get("submitted_at"))
                    if t and started and t >= started:
                        evidence_times.append(t)
            for rc in review_comments:
                if provider_for(rc.get("user", {}).get("login")) == name and rc.get("commit_id") == head_sha:
                    t = parse_ts(rc.get("created_at"))
                    if t and started and t >= started:
                        evidence_times.append(t)
            if evidence_times and started:
                latency = (min(evidence_times) - started).total_seconds()
            provider_recs[name] = {
                "state": info["state"],
                "required": name in parsed["required"],
                # Delivered per the orchestrator's own definition: a review or
                # review comment from the provider bound to this cycle's head
                # SHA at/after cycle start (latency evidence), or the state
                # comment's own provider_completed line. The state line alone
                # undercounts: it is a snapshot that only advances when a
                # later event re-triggers collect. (Check-run evidence is the
                # one orchestrator channel not reconstructed here.)
                "delivered": info["state"] == "provider_completed" or latency is not None,
                "cooldown": info["state"] == "provider_cooldown",
                "latency_sec": latency,
            }
        verdicts = {}
        for r in reviews:
            p = provider_for(r.get("user", {}).get("login"))
            if p:
                verdicts.setdefault(p, {})
                verdicts[p][r.get("state", "")] = verdicts[p].get(r.get("state", ""), 0) + 1
        rc_counts = {}
        for rc in review_comments:
            p = provider_for(rc.get("user", {}).get("login"))
            if p:
                rc_counts[p] = rc_counts.get(p, 0) + 1
        records.append({
            "pr": pr["number"],
            "cycle_id": f.get("cycle_id"),
            "head_sha": head_sha,
            "cycle_started_at": f.get("cycle_started_at"),
            "state": f.get("state"),
            "ready": f.get("ready"),
            "author": (pr.get("user") or {}).get("login", ""),
            "author_class": f.get("context_author_class") or a_class,
            "primary_class": rec_ctx_primary,
            "classes": ctx["classes"],
            "docs_only": ctx["docs_only"],
            "generated_only": ctx["generated_only"],
            "size": {
                "files": pr.get("changed_files"),
                "additions": pr.get("additions"),
                "deletions": pr.get("deletions"),
            },
            "labels": labels,
            "providers": provider_recs,
            "verdicts": verdicts,
            "review_comment_counts": rc_counts,
            "issue_comment_volume": volume,
            "coderabbit_skipped_notice": coderabbit_skipped,
        })
    return records


def _blank_bucket():
    return {
        "cycles": 0, "required_cycles": 0, "delivered": 0,
        "delivery_rate": None, "cooldown_cycles": 0, "not_required_cycles": 0,
        "latencies_sec": [], "median_latency_sec": None,
    }


def aggregate(records, prs_examined, warnings, pr_extras=None):
    providers = {}

    def bucket(provider, ctx_key=None, author=None):
        entry = providers.setdefault(
            provider, {"totals": _blank_bucket(), "by_context": {}, "by_author_class": {}})
        if author is not None:
            return entry["by_author_class"].setdefault(author, _blank_bucket())
        if ctx_key is None:
            return entry["totals"]
        return entry["by_context"].setdefault(ctx_key, _blank_bucket())

    volume_by_provider_ctx = {}
    verdicts_by_provider = {}
    review_comments_by_provider = {}
    for rec in records:
        ctx_key = f"{rec['author_class']}/{rec['primary_class']}"
        for name, prec in rec["providers"].items():
            for b in (bucket(name), bucket(name, ctx_key), bucket(name, author=rec["author_class"])):
                b["cycles"] += 1
                if prec["required"]:
                    b["required_cycles"] += 1
                if prec["delivered"]:
                    b["delivered"] += 1
                if prec["cooldown"]:
                    b["cooldown_cycles"] += 1
                if prec["state"].startswith("not_required"):
                    b["not_required_cycles"] += 1
                if prec["latency_sec"] is not None:
                    b["latencies_sec"].append(prec["latency_sec"])
    # Verdicts, review comments and issue-comment volume are PR-level data
    # carried on every cycle record of that PR: count them once per PR.
    seen_pr = set()
    for rec in records:
        if rec["pr"] in seen_pr:
            continue
        seen_pr.add(rec["pr"])
        for p, states in rec["verdicts"].items():
            v = verdicts_by_provider.setdefault(p, {})
            for s, n in states.items():
                v[s] = v.get(s, 0) + n
        for p, n in rec["review_comment_counts"].items():
            review_comments_by_provider[p] = review_comments_by_provider.get(p, 0) + n
        ctx_key = f"{rec['author_class']}/{rec['primary_class']}"
        for p, n in rec["issue_comment_volume"].items():
            for key in (p, f"{p}|{ctx_key}"):
                volume_by_provider_ctx[key] = volume_by_provider_ctx.get(key, 0) + n
    # Providers seen only in verdicts/volume (e.g. ECC, which the orchestrator
    # does not track) still get an entry so their stats are not dropped.
    for p in set(verdicts_by_provider) | set(review_comments_by_provider) | {
        k for k in volume_by_provider_ctx if "|" not in k
    }:
        bucket(p)
    bucket("ecc")  # the findings section below always attaches to this entry
    for name, entry in providers.items():
        for b in [entry["totals"], *entry["by_context"].values(), *entry["by_author_class"].values()]:
            if b["required_cycles"]:
                b["delivery_rate"] = round(b["delivered"] / b["required_cycles"], 4)
            if b["latencies_sec"]:
                b["median_latency_sec"] = round(statistics.median(b["latencies_sec"]), 1)
            b["latencies_sec"] = len(b["latencies_sec"])
        entry["verdicts"] = verdicts_by_provider.get(name, {})
        entry["review_comments"] = review_comments_by_provider.get(name, 0)
        entry["issue_comments"] = volume_by_provider_ctx.get(name, 0)
        entry["issue_comments_by_context"] = {
            k.split("|", 1)[1]: v for k, v in volume_by_provider_ctx.items() if k.startswith(name + "|")
        }
    # ECC findings (round 2, option C): ECC is comment-only, so delivery
    # rate is the wrong axis for it. Count its pr-audit conclusions instead:
    # action_required audits are findings; a finding leaves the "open"
    # bucket when its PR closes (dispositioned or moot — the PR state is
    # the proxy, stated here so nobody reads more into it than that).
    findings = {
        "audit_comments": 0, "findings_action_required": 0,
        "findings_on_open_prs": 0, "findings_on_closed_prs": 0,
        "current_head_findings": 0, "prs_with_findings": 0, "gates": {},
    }
    for ex in (pr_extras or []):
        audits = ex.get("ecc_audits") or []
        if not audits:
            continue
        findings["audit_comments"] += len(audits)
        flagged = [a for a in audits if a.get("conclusion") == "action_required"]
        for a in audits:
            g = findings["gates"].setdefault(
                a["gate"], {"audits": 0, "findings_action_required": 0})
            g["audits"] += 1
            if a.get("conclusion") == "action_required":
                g["findings_action_required"] += 1
        if flagged:
            findings["prs_with_findings"] += 1
            findings["findings_action_required"] += len(flagged)
            if ex.get("pr_state") == "open":
                findings["findings_on_open_prs"] += len(flagged)
            else:
                findings["findings_on_closed_prs"] += len(flagged)
            findings["current_head_findings"] += sum(
                1 for a in flagged if a.get("commit") == ex.get("head_sha"))
    providers["ecc"]["findings"] = findings
    return {
        "schema": "reviewer-metrics/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": {"prs_examined": prs_examined, "cycles": len(records)},
        "providers": providers,
        "cycles": records,
        "warnings": warnings,
    }


class ApiClient:
    def __init__(self, repo, token):
        self.repo = repo
        self.token = token

    def get(self, path):
        req = urllib.request.Request(
            f"https://api.github.com/repos/{self.repo}{path}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())


def collect(client, limit):
    warnings = []
    prs = client.get(f"/pulls?state=all&sort=updated&direction=desc&per_page={min(limit, 100)}")
    records = []
    pr_extras = []
    examined = 0
    for stub in prs[:limit]:
        number = stub["number"]
        try:
            pr = client.get(f"/pulls/{number}")
            comments = client.get(f"/issues/{number}/comments?per_page=100")
            pr_extras.append({
                "pr": number,
                "pr_state": pr.get("state"),
                "head_sha": (pr.get("head") or {}).get("sha", ""),
                "ecc_audits": parse_ecc_audits(comments),
            })
            if not any(STATE_MARKER in (c.get("body") or "") for c in comments):
                examined += 1
                continue
            reviews = client.get(f"/pulls/{number}/reviews?per_page=100")
            review_comments = client.get(f"/pulls/{number}/comments?per_page=100")
            files = client.get(f"/pulls/{number}/files?per_page=100")
            paths = [f.get("filename", "") for f in files]
            records.extend(build_cycle_records(pr, comments, reviews, review_comments, paths))
            examined += 1
        except Exception as exc:  # partial collection beats no collection
            warnings.append(f"pr {number}: {exc}")
    return aggregate(records, examined, warnings, pr_extras)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="timerloggedout-spec/termux-monorepo")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--out", default="reviewer-metrics.json")
    args = ap.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN/GITHUB_TOKEN not set", file=sys.stderr)
        return 2
    result = collect(ApiClient(args.repo, token), args.limit)
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    print(f"wrote {args.out}: {result['window']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
