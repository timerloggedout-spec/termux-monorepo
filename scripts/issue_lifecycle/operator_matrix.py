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

def _request(method: str, path: str, token: str, repo: str):
    url = f"{API}/repos/{repo}{path}" if path.startswith("/") else f"{API}/{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", USER_AGENT)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            if e.code in (403, 429) and "rate limit" in detail.lower() and attempt < 4:
                delay = min(5 * 2**attempt, 60)
                print(f"rate limit on {path}; retry {attempt + 1}/4 in {delay}s", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"GitHub API error: {method} {path} -> HTTP {e.code}: {detail}", file=sys.stderr)
            raise SystemExit(1)
    raise SystemExit(1)


def _paged(path: str, token: str, repo: str) -> list:
    out, page = [], 1
    while True:
        batch = _request("GET", f"{path}&per_page=100&page={page}" if "?" in path else f"{path}?per_page=100&page={page}", token, repo)
        if not batch:
            break
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return out


def _gates_for_sha(sha: str, token: str, repo: str) -> dict:
    cr = _request("GET", f"/commits/{sha}/check-runs?per_page=100", token, repo)
    gates: dict[str, str] = {}
    for run in cr.get("check_runs", []):
        if run["name"] == GATE_HYGIENE:
            gates["hygiene"] = run.get("conclusion") or run["status"]
        if "termux smoke" in run["name"] and "smoke" not in gates:
            gates["smoke"] = run.get("conclusion") or run["status"]
    return gates


def fetch_snapshot(repo: str, token: str) -> dict:
    items = _paged("/issues?state=open&sort=created&direction=asc", token, repo)
    issues, prs = [], []
    for x in items:
        base = {
            "number": x["number"],
            "title": x["title"],
            "labels": [l["name"] for l in x.get("labels", [])],
            "created_at": x["created_at"],
            "updated_at": x["updated_at"],
        }
        if "pull_request" not in x:
            base["assignees"] = len(x.get("assignees", []))
            base["milestone"] = bool(x.get("milestone"))
            issues.append(base)
            continue
        pr = _request("GET", f"/pulls/{x['number']}", token, repo)
        base.update(
            {
                "head_sha": pr["head"]["sha"],
                "mergeable": pr.get("mergeable"),
                "mergeable_state": pr.get("mergeable_state"),
                "draft": pr.get("draft"),
                "gates": _gates_for_sha(pr["head"]["sha"], token, repo),
            }
        )
        prs.append(base)
    tip = _request("GET", "/commits?sha=master&per_page=1", token, repo)[0]
    master = {"sha": tip["sha"], "gates": _gates_for_sha(tip["sha"], token, repo)}
    return {"master": master, "issues": issues, "prs": prs}


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
