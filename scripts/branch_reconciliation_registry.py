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



SURFACE_KINDS = {
    "commit": {"commit"},
    "issue": {"issue"},
    "comment": {"issue_comment", "review_comment"},
    "review": {"review"},
    "file": {"file"},
    "symbol": {"symbol"},
    "scope": {"scope"},
    "label": {"label"},
}
ALL_SURFACES = {"branch", "pull-request", *SURFACE_KINDS}
PROFILE_SURFACES = {
    "reconciliation": {"branch", "pull-request"},
    "delivery": {"branch", "pull-request", "commit", "issue", "comment", "review"},
    "architecture": {"file", "symbol", "scope", "label"},
    "full": set(ALL_SURFACES),
}


def selected_surfaces(profiles: list[str], explicit: list[str], include_ast: bool, include_similarity: bool) -> set[str]:
    selected = set().union(*(PROFILE_SURFACES[name] for name in profiles)) if profiles else set()
    selected.update(explicit)
    if include_ast:
        selected.update({"file", "symbol"})
    if include_similarity:
        selected.add("file")
    return selected or set(PROFILE_SURFACES["reconciliation"])


def matches_queries(record: Any, clauses: list[str], mode: str = "all") -> bool:
    if not clauses:
        return True
    haystack = json.dumps(record, sort_keys=True, ensure_ascii=False).casefold()
    hits = [clause.casefold() in haystack for clause in clauses]
    return all(hits) if mode == "all" else any(hits)


def load_graph_projection(index_dir: Path, surfaces: set[str], clauses: list[str], mode: str,
                          max_results: int, include_similarity: bool) -> dict[str, Any]:
    def read_jsonl(filename: str) -> list[dict[str, Any]]:
        path = index_dir / filename
        if not path.is_file():
            raise ValueError(f"graph index artifact is missing: {path}")
        rows = []
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number} contains invalid JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{number} must contain JSON objects")
            rows.append(row)
        return rows

    requested_kinds = set().union(*(SURFACE_KINDS.get(surface, set()) for surface in surfaces))
    nodes = [
        node for node in read_jsonl("nodes.jsonl")
        if node.get("kind") in requested_kinds and matches_queries(node, clauses, mode)
    ][:max_results]
    visible_ids = {str(node.get("id") or f"{node.get('kind')}:{node.get('external_id')}") for node in nodes}
    candidates: list[dict[str, Any]] = []
    if include_similarity:
        for edge in read_jsonl("edges.jsonl"):
            if edge.get("classification") != "candidate":
                continue
            if edge.get("source") in visible_ids or edge.get("target") in visible_ids:
                candidates.append(edge)
                if len(candidates) >= max_results:
                    break
    counts: dict[str, int] = {}
    for node in nodes:
        kind = str(node.get("kind", "unknown"))
        counts[kind] = counts.get(kind, 0) + 1
    return {
        "index": str(index_dir),
        "node_count": len(nodes),
        "node_counts_by_kind": dict(sorted(counts.items())),
        "nodes": nodes,
        "similarity_candidate_count": len(candidates),
        "similarity_candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repository")
    parser.add_argument("--default-branch", required=True)
    parser.add_argument("--output-dir", default="artifacts/branch-reconciliation")
    parser.add_argument("--query", action="append", default=[], metavar="CLAUSE",
                        help="Repeatable case-insensitive text clause; combine with --query-mode")
    parser.add_argument("--query-mode", choices=("all", "any"), default="all",
                        help="Require every query clause (all) or at least one (any)")
    parser.add_argument("--surface", action="append", choices=sorted(ALL_SURFACES), default=[],
                        help="Repeatable output surface selector")
    parser.add_argument("--profile", action="append", choices=sorted(PROFILE_SURFACES), default=[],
                        help="Repeatable composable analysis profile")
    parser.add_argument("--graph-index", type=Path,
                        help="Existing CRG index directory containing nodes.jsonl and edges.jsonl")
    parser.add_argument("--ast", action="store_true",
                        help="Include CRG file and Python AST symbol surfaces")
    parser.add_argument("--similarity", action="store_true",
                        help="Include existing CRG candidate similarity/co-change edges")
    parser.add_argument("--max-results", type=int, default=1000,
                        help="Maximum graph nodes and candidate edges in the report")
    args = parser.parse_args()
    if args.max_results < 1:
        parser.error("--max-results must be positive")
    surfaces = selected_surfaces(args.profile, args.surface, args.ast, args.similarity)
    graph_surfaces = surfaces & set(SURFACE_KINDS)
    if (graph_surfaces or args.similarity) and args.graph_index is None:
        parser.error("graph-backed surfaces, --ast, and --similarity require --graph-index")

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

    if args.query:
        records = [
            row for row in records
            if matches_queries({"branch": row, "pull_requests": row["pull_requests"]}, args.query, args.query_mode)
        ]
        for row in records:
            row["pull_requests"] = [
                pr for pr in row["pull_requests"]
                if matches_queries(pr, args.query, args.query_mode)
            ] or row["pull_requests"] if matches_queries(row, args.query, args.query_mode) else []

    graph_projection = None
    if graph_surfaces:
        graph_projection = load_graph_projection(
            args.graph_index, graph_surfaces, args.query, args.query_mode, args.max_results, args.similarity
        )
    elif args.similarity:
        graph_projection = load_graph_projection(
            args.graph_index, {"file"}, args.query, args.query_mode, args.max_results, True
        )

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    report = {
        "schema": "branch-reconciliation-registry/v1",
        "repository": args.repo,
        "default_branch": args.default_branch,
        "generated_at": now,
        "inventory_complete_for_api_pages": True,
        "branch_count": len(records),
        "pull_request_count": len(pulls),
        "selection": {
            "profiles": args.profile,
            "surfaces": sorted(surfaces),
            "queries": args.query,
            "query_mode": args.query_mode,
            "ast_enabled": args.ast,
            "similarity_enabled": args.similarity,
            "max_results": args.max_results,
        },
        "graph": graph_projection,
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
        f"- Selected surfaces: **{', '.join(sorted(surfaces))}**",
        f"- Query clauses: **{len(args.query)}** ({args.query_mode})",
        f"- Graph nodes: **{graph_projection['node_count'] if graph_projection else 0}**",
        f"- Similarity candidates: **{graph_projection['similarity_candidate_count'] if graph_projection else 0}**",
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
