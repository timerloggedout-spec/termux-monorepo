"""Operator Matrix generator (issue-lifecycle lane).

The Operator Matrix (issue #175) is the repo's priority view over the
open inventory. Its record used to be a hand-edited issue body, and a
Projects v2 board was kept in step by a per-event sync workflow
(ops-operator-matrix-project-sync) — 495 runs, all no-ops while its
prerequisites were missing, and a project-scoped token dependency
even once lit.

This generator is the replacement method: derive the matrix from the
live inventory and stamp it into the repo as generated files
(docs/ops/generated/operator-matrix.{json,md}), refreshed by a weekly
workflow that opens one PR (registration-monikers pattern). No board,
no project token, no per-event runs; the output is versioned,
diffable, and re-derivable at any time.

Classification uses the #175 lane vocabulary where it is mechanically
derivable from gate evidence, and says so where it is not:

- EXTRACT    — both dual gates green on the PR head AND mergeable.
- CANDIDATE  — both dual gates green on the PR head, merge state not
               clean (not mergeable / dirty / draft).
- NEED_EVIDENCE — anything else (a gate failed, is missing, or has
               not reported). The honest default.
- SUPERSEDE  — never auto-emitted: supersession is an operator
               judgment about duplicate/stale work, not a signal the
               API carries. The matrix counts 0 and says why.

The dual gates are the repo's functional gate pair: the
`hygiene + portability gate` check and the termux smoke check
(repo-gate family), per the operator rules on #175 (merges must pass
repo_gate + termux_smoke on the head SHA; advisory reviewers are
non-gate and are not read here).

Usage:
    operator_matrix.py --fetch            # live via GITHUB_TOKEN
    operator_matrix.py --from-snapshot snapshot.json
    operator_matrix.py --check --from-snapshot snapshot.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
DEFAULT_REPO = "timerloggedout-spec/termux-monorepo"
USER_AGENT = "termux-monorepo-operator-matrix"
GATE_HYGIENE = "hygiene + portability gate"
SCHEMA = "operator-matrix/v1"

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "docs" / "ops" / "generated" / "operator-matrix.json"
OUT_MD = ROOT / "docs" / "ops" / "generated" / "operator-matrix.md"

# Label-family rules, first match wins. Families are the repo's working
# programmes as they appear in the label taxonomy; an issue with no
# matching label is "unfiled" (or "unlabelled" when it has none at all).
FAMILY_RULES = [
    ("delphi", lambda labels: any(l.startswith("delphi") for l in labels)),
    ("quota", lambda labels: any("quota" in l for l in labels)),
    ("temporal", lambda labels: "temporal" in labels),
    ("mesh", lambda labels: "Integrations" in labels),
    ("security", lambda labels: "security" in labels),
    ("ci", lambda labels: "ci" in labels),
    ("providers", lambda labels: "Providers" in labels),
    ("proposal", lambda labels: "proposal" in labels),
    ("research", lambda labels: "research" in labels),
]


def lane_family(labels: list[str]) -> str:
    if not labels:
        return "unlabelled"
    for name, rule in FAMILY_RULES:
        if rule(labels):
            return name
    return "other"


def gate_state(gates: dict, key: str) -> str:
    return gates.get(key) or "not_reported"


def classify_pr(pr: dict) -> str:
    """#175 vocabulary from dual-gate evidence on the PR head."""
    gates = pr.get("gates", {})
    green = gate_state(gates, "hygiene") == "success" and gate_state(gates, "smoke") == "success"
    if not green:
        return "NEED_EVIDENCE"
    if pr.get("mergeable") is True and pr.get("mergeable_state") in ("clean", "unstable") and not pr.get("draft"):
        return "EXTRACT"
    return "CANDIDATE"


def build_matrix(snapshot: dict, generated_at: str) -> dict:
    prs = []
    class_counts = {"EXTRACT": 0, "CANDIDATE": 0, "NEED_EVIDENCE": 0, "SUPERSEDE": 0}
    for pr in snapshot.get("prs", []):
        cls = classify_pr(pr)
        class_counts[cls] += 1
        prs.append(
            {
                "number": pr["number"],
                "title": pr["title"],
                "class": cls,
                "family": lane_family(pr.get("labels", [])),
                "labels": pr.get("labels", []),
                "head_sha": (pr.get("head_sha") or "")[:10],
                "mergeable_state": pr.get("mergeable_state"),
                "gates": {
                    "hygiene": gate_state(pr.get("gates", {}), "hygiene"),
                    "smoke": gate_state(pr.get("gates", {}), "smoke"),
                },
                "updated_at": pr.get("updated_at"),
            }
        )
    prs.sort(key=lambda r: (r["class"] != "EXTRACT", r["class"] != "CANDIDATE", r["number"]))

    families: dict[str, dict] = {}
    for issue in snapshot.get("issues", []):
        fam = lane_family(issue.get("labels", []))
        families.setdefault(fam, {"issues": 0, "unlabelled_numbers": []})
        families[fam]["issues"] += 1
        if fam == "unlabelled":
            families[fam]["unlabelled_numbers"].append(issue["number"])
    for row in prs:
        families.setdefault(row["family"], {"issues": 0, "unlabelled_numbers": []})
        families[row["family"]].setdefault("prs", 0)
        families[row["family"]]["prs"] = families[row["family"]].get("prs", 0) + 1

    master = snapshot.get("master", {})
    master_gates = {
        "hygiene": gate_state(master.get("gates", {}), "hygiene"),
        "smoke": gate_state(master.get("gates", {}), "smoke"),
    }
    functional_gate = (
        "GREEN" if master_gates["hygiene"] == "success" and master_gates["smoke"] == "success" else "NOT ESTABLISHED"
    )

    return {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "master": {"sha": (master.get("sha") or "")[:10], "gates": master_gates, "functional_gate": functional_gate},
        "counts": {
            "open_issues": len(snapshot.get("issues", [])),
            "open_prs": len(prs),
            "pr_classes": class_counts,
        },
        "supersede_note": (
            "SUPERSEDE is never auto-emitted: supersession is an operator judgment "
            "about duplicate or stale work, not a signal the API carries."
        ),
        "families": dict(sorted(families.items())),
        "prs": prs,
        "issues_unlabelled": sorted(families.get("unlabelled", {}).get("unlabelled_numbers", [])),
    }


def validate_matrix(m: dict) -> None:
    """Stamp-guard: refuse outputs that cannot be the real inventory.

    The first automated cut (2026-10-28) stamped "0 issues, 96 PRs"
    because the workflow token lacked issues:read and the endpoint
    silently returned only PRs. A repo with open PRs and zero open
    issues is not credible here; fail loudly instead of stamping it.
    """
    c = m["counts"]
    if c["open_prs"] > 0 and c["open_issues"] == 0:
        raise ValueError("implausible inventory: open PRs but zero open issues (token scope?)")


def render_md(m: dict) -> str:
    c = m["counts"]
    lines = [
        "# Operator Matrix (generated)",
        "",
        f"Schema `{m['schema']}` · generated {m['generated_at']} · "
        f"derived from the live inventory by `scripts/issue_lifecycle/operator_matrix.py`.",
        "Method: docs/ops/ISSUE-LIFECYCLE.md (Operator Matrix method). "
        "Vocabulary: issue #175 (EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE).",
        "",
        f"**Master functional gate:** {m['master']['functional_gate']} on `{m['master']['sha']}` "
        f"(hygiene: {m['master']['gates']['hygiene']}, smoke: {m['master']['gates']['smoke']}). "
        "A tip is evidence for itself only; promotion rules live on #175.",
        "",
        f"**Open inventory:** {c['open_issues']} issues, {c['open_prs']} PRs. "
        f"PR classes: EXTRACT {c['pr_classes']['EXTRACT']} / CANDIDATE {c['pr_classes']['CANDIDATE']} / "
        f"NEED_EVIDENCE {c['pr_classes']['NEED_EVIDENCE']} / SUPERSEDE {c['pr_classes']['SUPERSEDE']}.",
        "",
        f"_{m['supersede_note']}_",
        "",
        "## PR classes",
        "",
        "| PR | Class | Family | Head | Hygiene | Smoke | Mergeable | Title |",
        "|----|-------|--------|------|---------|-------|-----------|-------|",
    ]
    for r in m["prs"]:
        title = r["title"].replace("|", "\\|")[:80]
        lines.append(
            f"| #{r['number']} | {r['class']} | {r['family']} | `{r['head_sha']}` | "
            f"{r['gates']['hygiene']} | {r['gates']['smoke']} | {r['mergeable_state']} | {title} |"
        )
    lines += ["", "## Families (open)", "", "| Family | Issues | PRs |", "|--------|--------|-----|"]
    for fam, row in m["families"].items():
        lines.append(f"| {fam} | {row.get('issues', 0)} | {row.get('prs', 0)} |")
    lines += [
        "",
        f"**Unlabelled open issues ({len(m['issues_unlabelled'])}):** "
        + (", ".join(f"#{n}" for n in m["issues_unlabelled"]) or "none")
        + " — worked oldest-first by the issue-lifecycle lane pass.",
        "",
    ]
    return "\n".join(lines)


# --- live fetch (stdlib only; GITHUB_TOKEN from the environment) ---
#
# GraphQL, deliberately: the first version fetched over REST and
# needed ~200 calls per run (issue pages + one detail + one
# check-runs call per PR), which died on the shared Actions
# installation rate limit in hot hours (run 40752171030, HTTP 403
# after retries). The GraphQL shape below needs ~5 calls total for
# the same snapshot.

_CONTEXT_FIELDS = """
  __typename
  ... on CheckRun { name conclusion status }
  ... on StatusContext { context state }
"""

_ISSUES_Q = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    issues(first: 100, after: $cursor, states: OPEN,
           orderBy: {field: CREATED_AT, direction: ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title createdAt updatedAt
        labels(first: 20) { nodes { name } }
        assignees(first: 1) { totalCount }
        milestone { number }
      }
    }
  }
}
"""

_PRS_Q = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 40, after: $cursor, states: OPEN,
                 orderBy: {field: CREATED_AT, direction: ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title createdAt updatedAt isDraft mergeable mergeStateStatus headRefOid
        labels(first: 20) { nodes { name } }
        commits(last: 1) { nodes { commit {
          statusCheckRollup { contexts(first: 50) { nodes { %s } } }
        } } }
      }
    }
  }
}
""" % _CONTEXT_FIELDS

_MASTER_Q = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    ref(qualifiedName: "refs/heads/master") {
      target { ... on Commit {
        oid
        statusCheckRollup { contexts(first: 50) { nodes { %s } } }
      } }
    }
  }
}
""" % _CONTEXT_FIELDS


def _graphql(query: str, variables: dict, token: str) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(f"{API}/graphql", data=body, method="POST")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            if e.code in (403, 429) and "rate limit" in detail.lower() and attempt < 4:
                delay = min(5 * 2**attempt, 60)
                print(f"rate limit on graphql; retry {attempt + 1}/4 in {delay}s", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"GitHub API error: POST /graphql -> HTTP {e.code}: {detail}", file=sys.stderr)
            raise SystemExit(1)
        errors = payload.get("errors") or []
        if errors:
            text = json.dumps(errors)[:500]
            if "RATE_LIMITED" in text and attempt < 4:
                delay = min(5 * 2**attempt, 60)
                print(f"rate limit on graphql; retry {attempt + 1}/4 in {delay}s", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"GitHub GraphQL errors: {text}", file=sys.stderr)
            raise SystemExit(1)
        return payload.get("data") or {}
    raise SystemExit(1)


def _gates_from_contexts(contexts: list) -> dict:
    gates: dict[str, str] = {}
    for ctx in contexts or []:
        if ctx.get("__typename") == "CheckRun":
            name = ctx.get("name") or ""
            value = (ctx.get("conclusion") or ctx.get("status") or "").lower()
        else:
            name = ctx.get("context") or ""
            value = (ctx.get("state") or "").lower()
        if name == GATE_HYGIENE:
            gates["hygiene"] = value
        if "termux smoke" in name and "smoke" not in gates:
            gates["smoke"] = value
    return gates


def _labels(node: dict) -> list:
    return [l["name"] for l in ((node.get("labels") or {}).get("nodes") or [])]


def shape_snapshot(issue_nodes: list, pr_nodes: list, master_target: dict) -> dict:
    """Pure shaping from GraphQL nodes to the snapshot schema."""
    issues = [
        {
            "number": x["number"],
            "title": x["title"],
            "labels": _labels(x),
            "created_at": x["createdAt"],
            "updated_at": x["updatedAt"],
            "assignees": (x.get("assignees") or {}).get("totalCount", 0),
            "milestone": bool(x.get("milestone")),
        }
        for x in issue_nodes
    ]
    prs = []
    for x in pr_nodes:
        commits = ((x.get("commits") or {}).get("nodes") or [])
        rollup = {}
        if commits:
            rollup = (commits[0].get("commit") or {}).get("statusCheckRollup") or {}
        contexts = (rollup.get("contexts") or {}).get("nodes") or []
        prs.append(
            {
                "number": x["number"],
                "title": x["title"],
                "labels": _labels(x),
                "created_at": x["createdAt"],
                "updated_at": x["updatedAt"],
                "head_sha": x.get("headRefOid"),
                "mergeable": x.get("mergeable") == "MERGEABLE",
                "mergeable_state": (x.get("mergeStateStatus") or "UNKNOWN").lower(),
                "draft": bool(x.get("isDraft")),
                "gates": _gates_from_contexts(contexts),
            }
        )
    contexts = ((master_target.get("statusCheckRollup") or {}).get("contexts") or {}).get("nodes") or []
    master = {"sha": master_target.get("oid"), "gates": _gates_from_contexts(contexts)}
    return {"master": master, "issues": issues, "prs": prs}


def _paginate(query: str, key: str, owner: str, name: str, token: str) -> list:
    nodes, cursor = [], None
    while True:
        data = _graphql(query, {"owner": owner, "name": name, "cursor": cursor}, token)
        conn = (data.get("repository") or {}).get(key) or {}
        nodes.extend(conn.get("nodes") or [])
        page = conn.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            return nodes
        cursor = page.get("endCursor")


def fetch_snapshot(repo: str, token: str) -> dict:
    owner, name = repo.split("/", 1)
    issue_nodes = _paginate(_ISSUES_Q, "issues", owner, name, token)
    pr_nodes = _paginate(_PRS_Q, "pullRequests", owner, name, token)
    data = _graphql(_MASTER_Q, {"owner": owner, "name": name}, token)
    target = ((data.get("repository") or {}).get("ref") or {}).get("target") or {}
    return shape_snapshot(issue_nodes, pr_nodes, target)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true", help="fetch the live snapshot via GITHUB_TOKEN")
    ap.add_argument("--from-snapshot", metavar="FILE", help="build from a saved snapshot JSON")
    ap.add_argument("--check", action="store_true", help="exit 1 if generated outputs differ")
    ap.add_argument("--generated-at", default="", help="timestamp stamp (default: snapshot time or now)")
    args = ap.parse_args()

    if args.fetch:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            print("GITHUB_TOKEN (or GH_TOKEN) is required for --fetch", file=sys.stderr)
            return 2
        repo = os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO
        snapshot = fetch_snapshot(repo, token)
    elif args.from_snapshot:
        snapshot = json.loads(Path(args.from_snapshot).read_text())
    else:
        print("one of --fetch or --from-snapshot is required", file=sys.stderr)
        return 2

    generated_at = args.generated_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    matrix = build_matrix(snapshot, generated_at)
    try:
        validate_matrix(matrix)
    except ValueError as e:
        print(f"operator-matrix: refusing to stamp: {e}", file=sys.stderr)
        return 1
    json_text = json.dumps(matrix, indent=2, sort_keys=True) + "\n"
    md_text = render_md(matrix)

    if args.check:
        ok = OUT_JSON.exists() and OUT_JSON.read_text() == json_text and OUT_MD.exists() and OUT_MD.read_text() == md_text
        print("operator-matrix outputs are current" if ok else "operator-matrix outputs are STALE")
        return 0 if ok else 1

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json_text)
    OUT_MD.write_text(md_text)
    c = matrix["counts"]
    print(
        f"operator-matrix: {c['open_issues']} issues, {c['open_prs']} PRs "
        f"(EXTRACT {c['pr_classes']['EXTRACT']} / CANDIDATE {c['pr_classes']['CANDIDATE']} / "
        f"NEED_EVIDENCE {c['pr_classes']['NEED_EVIDENCE']}); master gate {matrix['master']['functional_gate']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
