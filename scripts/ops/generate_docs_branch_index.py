#!/usr/bin/env python3
"""Generate docs/ops/DOCS-BRANCH-INDEX.md from GitHub API + local registry.

stdlib-only. Intended for CI (GITHUB_TOKEN) or local with GH_TOKEN / GITHUB_TOKEN.

Usage:
  python3 scripts/ops/generate_docs_branch_index.py
  python3 scripts/ops/generate_docs_branch_index.py --check   # exit 1 if stale
  python3 scripts/ops/generate_docs_branch_index.py --stdout
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "docs" / "ops" / "DOCS-BRANCH-INDEX.md"
REGISTRY_PATH = ROOT / "docs" / "proposals" / "registry.yaml"

DOCS_REF_RE = re.compile(r"^refs/heads/(docs/.+|docs-lane-.+)$")
MARKER_BEGIN = "<!-- BEGIN:docs-branch-index (generated; do not edit) -->"
MARKER_END = "<!-- END:docs-branch-index -->"


def _token() -> str:
    return (
        os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or os.environ.get("GITHUB_API_TOKEN")
        or ""
    )


def _repo_slug() -> tuple[str, str]:
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER") or "timerloggedout-spec"
    repo = os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")
    if "/" in repo:
        owner, name = repo.split("/", 1)
    else:
        name = repo
    return owner, name


def _api_get(url: str, token: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "termux-monorepo-docs-branch-index",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _paginate(url: str, token: str, per_page: int = 100) -> list[Any]:
    items: list[Any] = []
    page = 1
    while True:
        sep = "&" if "?" in url else "?"
        page_url = f"{url}{sep}per_page={per_page}&page={page}"
        batch = _api_get(page_url, token)
        if not isinstance(batch, list):
            break
        items.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
        if page > 20:
            break
    return items


def load_registry_branch_map() -> dict[str, list[str]]:
    """Map branch name -> list of proposal ids that reference it."""
    mapping: dict[str, list[str]] = {}
    if not REGISTRY_PATH.is_file():
        return mapping
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    # Lightweight parse: avoid requiring PyYAML in CI for this job.
    current_id: str | None = None
    in_related = False
    for line in text.splitlines():
        m = re.match(r"^\s+- id:\s*(\S+)", line)
        if m:
            current_id = m.group(1).strip()
            in_related = False
            continue
        if current_id and re.match(r"^\s+source_branch:\s*(\S+)", line):
            br = re.match(r"^\s+source_branch:\s*(\S+)", line)
            if br:
                mapping.setdefault(br.group(1).strip(), []).append(current_id)
            continue
        if current_id and re.match(r"^\s+related_branches:\s*", line):
            rest = line.split(":", 1)[1].strip()
            in_related = rest in ("", "[]") or rest.startswith("[")
            if rest.startswith("[") and rest.endswith("]"):
                inner = rest[1:-1].strip()
                if inner:
                    for part in inner.split(","):
                        name = part.strip().strip("'\"")
                        if name:
                            mapping.setdefault(name, []).append(current_id)
                in_related = False
            continue
        if in_related and current_id:
            m2 = re.match(r"^\s+-\s+(\S+)", line)
            if m2:
                mapping.setdefault(m2.group(1).strip(), []).append(current_id)
            elif re.match(r"^\s+\w+:", line):
                in_related = False
    return mapping


def fetch_docs_branches(owner: str, repo: str, token: str) -> list[dict[str, Any]]:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/matching-refs/heads/docs"
    refs = _api_get(url, token)
    if not isinstance(refs, list):
        refs = []
    # also docs-lane-*
    try:
        lane = _api_get(
            f"https://api.github.com/repos/{owner}/{repo}/git/matching-refs/heads/docs-lane",
            token,
        )
        if isinstance(lane, list):
            refs.extend(lane)
    except urllib.error.HTTPError:
        pass

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ref in refs:
        refname = ref.get("ref") or ""
        m = DOCS_REF_RE.match(refname)
        if not m:
            # matching-refs/heads/docs also returns docs/... only when prefix matches;
            # accept any refs/heads/docs*
            if not refname.startswith("refs/heads/docs"):
                continue
            name = refname[len("refs/heads/") :]
        else:
            name = m.group(1)
        if name in seen:
            continue
        seen.add(name)
        obj = ref.get("object") or {}
        sha = (obj.get("sha") or "")[:12]
        out.append({"name": name, "sha": sha, "full_sha": obj.get("sha") or ""})
    out.sort(key=lambda x: x["name"])
    return out


def fetch_open_docs_prs(owner: str, repo: str, token: str) -> dict[str, list[dict[str, Any]]]:
    """head branch name -> list of open PR summaries."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open"
    prs = _paginate(url, token)
    by_head: dict[str, list[dict[str, Any]]] = {}
    for pr in prs:
        head = (pr.get("head") or {}).get("ref") or ""
        if not (head.startswith("docs/") or head.startswith("docs-lane-")):
            continue
        by_head.setdefault(head, []).append(
            {
                "number": pr.get("number"),
                "title": (pr.get("title") or "").replace("|", "\\|"),
                "html_url": pr.get("html_url") or "",
                "draft": bool(pr.get("draft")),
                "base": ((pr.get("base") or {}).get("ref") or ""),
            }
        )
    return by_head


def render(
    branches: list[dict[str, Any]],
    prs_by_head: dict[str, list[dict[str, Any]]],
    registry_map: dict[str, list[str]],
    owner: str,
    repo: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    lines.append("# Docs-branch index")
    lines.append("")
    lines.append(
        "Automated inventory of remote `docs/*` (and `docs-lane-*`) branches for "
        "navigation and amendment tracking. Policy: debate lanes stay until "
        "promoted; master holds pointers — see `docs/CONSENSUS.md` §10 and #175."
    )
    lines.append("")
    lines.append(f"**Generated:** `{now}` UTC  ")
    lines.append(f"**Generator:** `scripts/ops/generate_docs_branch_index.py`  ")
    lines.append(f"**Repo:** `{owner}/{repo}`  ")
    lines.append(f"**Count:** {len(branches)} docs-lane branch(es)")
    lines.append("")
    lines.append("Do **not** hand-edit the generated table below. Amend via PR or registry.")
    lines.append("")
    lines.append(MARKER_BEGIN)
    lines.append("")
    lines.append(
        "| Branch | SHA | Open PR(s) | Registry proposal(s) | Notes |"
    )
    lines.append("|--------|-----|------------|----------------------|-------|")

    for b in branches:
        name = b["name"]
        sha = b["sha"] or "—"
        branch_url = f"https://github.com/{owner}/{repo}/tree/{name}"
        prs = prs_by_head.get(name, [])
        if prs:
            pr_cell = ", ".join(
                f"[#{p['number']}]({p['html_url']})→`{p['base']}`"
                + (" (draft)" if p["draft"] else "")
                for p in prs
            )
        else:
            pr_cell = "—"
        props = registry_map.get(name, [])
        prop_cell = ", ".join(f"`{p}`" for p in props) if props else "—"
        notes = []
        if not prs and not props:
            notes.append("orphan lane")
        elif props and not prs:
            notes.append("registered; no open PR")
        elif prs and not props:
            notes.append("PR without registry link")
        note_cell = "; ".join(notes) if notes else ""
        lines.append(
            f"| [`{name}`]({branch_url}) | `{sha}` | {pr_cell} | {prop_cell} | {note_cell} |"
        )

    lines.append("")
    lines.append(MARKER_END)
    lines.append("")
    lines.append("## How this is maintained")
    lines.append("")
    lines.append("- **CI:** `.github/workflows/docs-branch-index.yml` (schedule + `workflow_dispatch`).")
    lines.append("- **Local:** `python3 scripts/ops/generate_docs_branch_index.py`")
    lines.append("- **Check freshness:** `python3 scripts/ops/generate_docs_branch_index.py --check`")
    lines.append("- **Promotion:** open a small PR from a docs lane → master; do not wholesale-merge.")
    lines.append("- **Registry:** `docs/proposals/registry.yaml` `related_branches` / `source_branch`.")
    lines.append("")
    lines.append("## Related")
    lines.append("")
    lines.append("- Issue #175 (actions / lane visibility)")
    lines.append("- `docs/CONSENSUS.md`")
    lines.append("- `docs/ops/LANE_CONSOLIDATION_SSOT.md`")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Exit 1 if on-disk index is stale")
    ap.add_argument("--stdout", action="store_true", help="Print markdown to stdout only")
    ap.add_argument("--out", type=Path, default=OUT_PATH, help="Output path")
    args = ap.parse_args()

    token = _token()
    owner, repo = _repo_slug()
    if not token:
        print("warning: no GITHUB_TOKEN/GH_TOKEN; API may rate-limit", file=sys.stderr)

    try:
        branches = fetch_docs_branches(owner, repo, token)
        prs_by_head = fetch_open_docs_prs(owner, repo, token)
    except urllib.error.HTTPError as e:
        print(f"GitHub API error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"failed: {e}", file=sys.stderr)
        return 2

    registry_map = load_registry_branch_map()
    body = render(branches, prs_by_head, registry_map, owner, repo)

    if args.stdout:
        sys.stdout.write(body)
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    existing = args.out.read_text(encoding="utf-8") if args.out.is_file() else ""

    def strip_timestamp(md: str) -> str:
        return re.sub(r"\*\*Generated:\*\* `[^`]+`", "**Generated:** `<ts>`", md)

    if args.check:
        if strip_timestamp(existing) != strip_timestamp(body):
            print("DOCS-BRANCH-INDEX.md is stale; regenerate.", file=sys.stderr)
            return 1
        print("DOCS-BRANCH-INDEX.md is up to date.")
        return 0

    if existing == body:
        print(f"unchanged: {args.out}")
        return 0

    args.out.write_text(body, encoding="utf-8")
    print(f"wrote {args.out} ({len(branches)} branches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
