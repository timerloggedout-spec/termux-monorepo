#!/usr/bin/env python3
"""Build living help-wanted status + Tribute ledger from evidence + live foreign PRs.

Writes status json/md AND apps/help-wanted-dashboard/data/status.json.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
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


def lane_git_history() -> list[dict]:
    paths = ['apps/help-wanted-dashboard/', 'docs/ops/HELP-WANTED-', '.agents/skills/help-wanted-lane/', '.github/workflows/help-wanted-', 'scripts/ci/help_wanted_']
    try:
        raw = subprocess.check_output(['git','log','--date=iso-strict','--format=%H%x09%aI%x09%an%x09%s','--',*paths], text=True, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return []
    history = []
    for line in raw.splitlines():
        parts = line.split('\t', 3)
        if len(parts) == 4:
            sha, date, author, subject = parts
            history.append({'sha': sha, 'short_sha': sha[:12], 'date': date, 'author': author, 'subject': subject, 'url': 'https://github.com/timerloggedout-spec/termux-monorepo/commit/' + sha})
    return history

def current_source_sha() -> str:
    value = os.environ.get('GITHUB_SHA') or os.environ.get('SOURCE_SHA')
    if value: return value
    try: return subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    except (OSError, subprocess.CalledProcessError): return ''

def live_foreign_prs(state: str = "open") -> list[dict]:
    q = f"author:{AUTHOR} is:pr is:{state} -repo:timerloggedout-spec/termux-monorepo"
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
                "state": state,
                "updated_at": it.get("updated_at"),
                "tribute": True,
            }
        )
    return out


def build_tributes(rows: list[dict], foreign_open: list[dict], foreign_closed: list[dict]) -> list[dict]:
    """Ledger: each upstream PR attempt is a tribute to the foreign maintainer."""
    by_pr: dict[str, dict] = {}
    for r in rows:
        pr = r.get("pr_url") or ""
        if not pr or "pull" not in pr:
            # followup may use issue=PR url
            issue = str(r.get("issue") or "")
            if "/pull/" in issue:
                pr = issue
            else:
                continue
        if AUTHOR in pr and "termux-monorepo" in pr:
            continue
        entry = by_pr.setdefault(
            pr,
            {
                "pr_url": pr,
                "kinds": [],
                "ok": True,
                "last_ts": r.get("ts"),
                "providers": [],
            },
        )
        entry["kinds"].append(r.get("kind"))
        entry["ok"] = entry["ok"] and bool(r.get("ok", True))
        if (r.get("ts") or "") >= (entry.get("last_ts") or ""):
            entry["last_ts"] = r.get("ts")
        if r.get("provider"):
            entry["providers"].append(r.get("provider"))
        if r.get("model"):
            entry["model"] = r.get("model")

    for p in foreign_open + foreign_closed:
        pr = p.get("html_url") or ""
        if not pr:
            continue
        entry = by_pr.setdefault(
            pr,
            {
                "pr_url": pr,
                "kinds": ["upstream_pr"],
                "ok": True,
                "last_ts": p.get("updated_at"),
                "providers": [],
            },
        )
        entry["repo"] = p.get("repo")
        entry["number"] = p.get("number")
        entry["title"] = p.get("title")
        entry["state"] = p.get("state")

    tributes = list(by_pr.values())
    tributes.sort(key=lambda x: x.get("last_ts") or "", reverse=True)
    return tributes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", default="docs/ops/generated/help-wanted-evidence")
    ap.add_argument("--out-md", default="docs/ops/generated/help-wanted-status.md")
    ap.add_argument("--out-json", default="docs/ops/generated/help-wanted-status.json")
    ap.add_argument("--dashboard-json", default="apps/help-wanted-dashboard/data/status.json")
    args = ap.parse_args()

    evid = Path(args.evidence_dir)
    rows: list[dict] = []
    if evid.is_dir():
        for p in sorted(evid.glob("*.jsonl")):
            rows.extend(load_jsonl(p))
    rows = [r for r in rows if not is_internal(str(r.get("issue") or ""))]

    by_issue: dict[str, list[dict]] = defaultdict(list)
    kinds = Counter()
    ok_c = Counter()
    for r in rows:
        issue = r.get("issue") or "(unknown)"
        by_issue[issue].append(r)
        kinds[r.get("kind") or "unknown"] += 1
        ok_c["ok" if r.get("ok") else "fail"] += 1

    foreign = live_foreign_prs("open")
    foreign_closed = live_foreign_prs("closed")
    tributes = build_tributes(rows, foreign, foreign_closed)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    history = lane_git_history()
    source_sha = current_source_sha()

    board = {
        "generated_at": now,
        "lane": "help-wanted",
        "project": "help-wanted-with-tribute",
        "receipts": len(rows),
        "kinds": dict(kinds),
        "outcomes": dict(ok_c),
        "foreign_open_prs": foreign,
        "foreign_open_count": len(foreign),
        "tributes": tributes,
        "tribute_count": len(tributes),
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
            "tribute": "each upstream PR is a contributor tribute to the foreign maintainer",
        },
        "live": {
            "dashboard": "https://timerloggedout-spec.github.io/help-wanted/",
            "githack": "https://raw.githack.com/timerloggedout-spec/termux-monorepo/master/apps/help-wanted-dashboard/index.html",
            "status_raw": "https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/docs/ops/generated/help-wanted-status.json",
            "tribute_doc": "docs/ops/HELP-WANTED-TRIBUTE.md",
        },
        "control_surface": {"schema_version":"help-wanted.control-surface.v2","source_sha":source_sha,"source_ref":os.environ.get("GITHUB_REF_NAME","local"),"history_complete":True,"history_count":len(history),"lane_paths":["apps/help-wanted-dashboard/","docs/ops/HELP-WANTED-*",".agents/skills/help-wanted-lane/",".github/workflows/help-wanted-*","scripts/ci/help_wanted_*"],"authority":"GitHub commits, PRs, issues, reviews, checks, Actions and evidence JSONL","projection_only":True,"deployment":[{"name":"GitHub Pages user site","url":"https://timerloggedout-spec.github.io/help-wanted/","role":"canonical public static ops UI"},{"name":"Vercel","role":"interactive deployment lane","verification":"provider deployment evidence required"},{"name":"Project Pages","url":"https://timerloggedout-spec.github.io/termux-monorepo/","role":"project hub, not dashboard twin"}]},
        "evolution": history,
        "pipeline": [
            "scout",
            "execute",
            "followup",
            "llm-assist",
            "rerequest",
            "status-refresh",
            "dashboard-deploy",
        ],
    }

    text = json.dumps(board, indent=2) + "\n"
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(text, encoding="utf-8")
    Path(args.dashboard_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.dashboard_json).write_text(text, encoding="utf-8")

    lines = [
        "# Help-Wanted Living Status · with Tribute",
        "",
        f"_Generated {now} UTC · receipts={len(rows)} · foreign_open={len(foreign)} · tributes={len(tributes)}_",
        "",
        "## Tributes (contributor ledger)",
        "",
    ]
    for t in tributes[:40]:
        label = t.get("repo") and f"{t.get('repo')}#{t.get('number')}" or t.get("pr_url")
        lines.append(
            f"- [{label}]({t.get('pr_url')}) · state={t.get('state', '?')} · {t.get('title') or ''}"
        )
    lines.extend(
        [
            "",
            "## Foreign open PRs",
            "",
        ]
    )
    for p in foreign:
        lines.append(f"- [{p.get('repo')}#{p.get('number')}]({p.get('html_url')}) — {p.get('title')}")
    lines.extend(
        [
            "",
            f"## Outcomes · ok={ok_c.get('ok', 0)} fail={ok_c.get('fail', 0)} kinds=`{dict(kinds)}`",
            "",
            "See docs/ops/HELP-WANTED-TRIBUTE.md",
            "",
        ]
    )
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "receipts": len(rows),
                "foreign_open": len(foreign),
                "tributes": len(tributes),
                "wrote": str(args.out_json),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
