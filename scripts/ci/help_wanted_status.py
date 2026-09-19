#!/usr/bin/env python3
"""Build living help-wanted status from evidence + live foreign PR search.

Writes status json/md AND copies into apps/help-wanted-dashboard/data/status.json
so Pages/CDN cannot serve a frozen snapshot while evidence advanced.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
AUTHOR = os.environ.get("HELP_WANTED_AUTHOR", "timerloggedout-spec")
TOKEN = (
    os.environ.get("OPERATOR_GITHUB_TOKEN")
    or os.environ.get("OPERATOR_TOKEN")
    or os.environ.get("ARCHWIZ_GITHUB_TOKEN")
    or os.environ.get("GITHUB_TOKEN")
    or ""
)
EXCLUDE = {"timerloggedout-spec/termux-monorepo"}


def api_get(path: str):
    url = path if path.startswith("http") else f"{API}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-help-wanted-status",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"api skip {path}: {e}")
        return None


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def is_internal(issue: str) -> bool:
    return "timerloggedout-spec/termux-monorepo" in (issue or "")


def live_foreign_prs() -> list[dict]:
    """Open PRs we authored outside the monorepo."""
    q = f"author:{AUTHOR} is:pr is:open -repo:timerloggedout-spec/termux-monorepo"
    data = api_get(f"/search/issues?q={urllib.parse.quote(q)}&per_page=50")
    if not data:
        return []
    out = []
    for it in data.get("items") or []:
        repo_url = it.get("repository_url") or ""
        parts = repo_url.rstrip("/").split("/")
        full = f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else ""
        if full in EXCLUDE:
            continue
        out.append(
            {
                "html_url": it.get("html_url"),
                "title": it.get("title"),
                "number": it.get("number"),
                "repo": full,
                "updated_at": it.get("updated_at"),
            }
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", default="docs/ops/generated/help-wanted-evidence")
    ap.add_argument("--out-md", default="docs/ops/generated/help-wanted-status.md")
    ap.add_argument("--out-json", default="docs/ops/generated/help-wanted-status.json")
    ap.add_argument(
        "--dashboard-json",
        default="apps/help-wanted-dashboard/data/status.json",
    )
    args = ap.parse_args()

    evid = Path(args.evidence_dir)
    rows: list[dict] = []
    if evid.is_dir():
        for p in sorted(evid.glob("*.jsonl")):
            rows.extend(load_jsonl(p))

    # Drop internal monorepo noise from board projection
    rows = [r for r in rows if not is_internal(str(r.get("issue") or ""))]

    by_issue: dict[str, list[dict]] = defaultdict(list)
    kinds = Counter()
    ok_c = Counter()
    for r in rows:
        issue = r.get("issue") or "(unknown)"
        by_issue[issue].append(r)
        kinds[r.get("kind") or "unknown"] += 1
        ok_c["ok" if r.get("ok") else "fail"] += 1

    foreign = live_foreign_prs()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    board = {
        "generated_at": now,
        "lane": "help-wanted",
        "receipts": len(rows),
        "kinds": dict(kinds),
        "outcomes": dict(ok_c),
        "foreign_open_prs": foreign,
        "foreign_open_count": len(foreign),
        "issues": {
            k: sorted(v, key=lambda x: x.get("ts") or "") for k, v in by_issue.items()
        },
        "policy": {
            "claim_idempotent": True,
            "skip_closed_issues": True,
            "primary": "upstream-pr",
            "fallback": "fork-notice",
            "foreign_only_followup": True,
            "exclude_monorepo": True,
        },
        "live": {
            "dashboard": "https://timerloggedout-spec.github.io/help-wanted/",
            "githack": "https://raw.githack.com/timerloggedout-spec/termux-monorepo/master/apps/help-wanted-dashboard/index.html",
            "status_raw": "https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/docs/ops/generated/help-wanted-status.json",
        },
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(board, indent=2) + "\n"
    out_json.write_text(text, encoding="utf-8")

    dash = Path(args.dashboard_json)
    dash.parent.mkdir(parents=True, exist_ok=True)
    dash.write_text(text, encoding="utf-8")

    lines = [
        "# Help-Wanted Living Status",
        "",
        f"_Generated {now} UTC · receipts={len(rows)} · foreign_open={len(foreign)}_",
        "",
        "## Foreign open PRs (live search)",
        "",
    ]
    if foreign:
        for p in foreign:
            lines.append(f"- [{p.get('repo')}#{p.get('number')}]({p.get('html_url')}) — {p.get('title')}")
    else:
        lines.append("- (none or API unavailable)")
    lines.extend(
        [
            "",
            "## Outcomes",
            f"- ok: **{ok_c.get('ok', 0)}** · fail: **{ok_c.get('fail', 0)}**",
            f"- kinds: `{dict(kinds)}`",
            "",
            "## Issues tracked (evidence)",
            "",
            "| Issue | Latest kind | ok | Last ts |",
            "|-------|-------------|----|---------|",
        ]
    )
    for issue, events in sorted(by_issue.items()):
        last = events[-1]
        lines.append(
            f"| {issue} | {last.get('kind')} | {last.get('ok')} | {last.get('ts')} |"
        )
    lines.append("")
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "receipts": len(rows),
                "foreign_open": len(foreign),
                "wrote": str(out_json),
                "dashboard": str(dash),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
