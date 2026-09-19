#!/usr/bin/env python3
"""Build living help-wanted status board from evidence JSONL + optional API.

Writes:
  docs/ops/generated/help-wanted-status.md
  docs/ops/generated/help-wanted-status.json

Human-review surface; feeds future Vercel dashboard. Does NOT admit MoneyBall.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--evidence-dir",
        default="docs/ops/generated/help-wanted-evidence",
    )
    ap.add_argument(
        "--out-md",
        default="docs/ops/generated/help-wanted-status.md",
    )
    ap.add_argument(
        "--out-json",
        default="docs/ops/generated/help-wanted-status.json",
    )
    args = ap.parse_args()

    evid = Path(args.evidence_dir)
    rows: list[dict] = []
    if evid.is_dir():
        for p in sorted(evid.glob("*.jsonl")):
            rows.extend(load_jsonl(p))

    by_issue: dict[str, list[dict]] = defaultdict(list)
    kinds = Counter()
    ok_c = Counter()
    for r in rows:
        issue = r.get("issue") or "(unknown)"
        by_issue[issue].append(r)
        kinds[r.get("kind") or "unknown"] += 1
        ok_c["ok" if r.get("ok") else "fail"] += 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    board = {
        "generated_at": now,
        "lane": "help-wanted",
        "receipts": len(rows),
        "kinds": dict(kinds),
        "outcomes": dict(ok_c),
        "issues": {
            k: sorted(v, key=lambda x: x.get("ts") or "") for k, v in by_issue.items()
        },
        "policy": {
            "claim_idempotent": True,
            "skip_closed_issues": True,
            "primary": "upstream-pr",
            "fallback": "fork-notice",
            "respect_maintainer_routing": True,
            "note": "Upstream-logic bugs on platform forks → prefer upstream repo when maintainer directs (e.g. codex-termux → openai/codex; feature delta → codex-vl).",
        },
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Help-Wanted Living Status",
        "",
        f"_Generated {now} UTC · receipts={len(rows)} · lane=help-wanted (Oversight)_",
        "",
        "## Policy (working well with others)",
        "",
        "1. **Claim once** — never re-post the claim marker if already present.",
        "2. **Skip closed issues** unless explicitly allowed.",
        "3. **PRIMARY** = upstream PR into the author's repo; **FALLBACK** = issue notice + fork branch.",
        "4. **Respect maintainer routing** — if maintainers say the defect is upstream logic, prefer the upstream repo (or their designated feature fork) over patching a parity fork.",
        "5. Stake PRs are placeholders; replace with real fixes or close when out of scope.",
        "",
        "## Outcomes",
        "",
        f"- ok: **{ok_c.get('ok', 0)}**",
        f"- fail: **{ok_c.get('fail', 0)}**",
        f"- kinds: `{dict(kinds)}`",
        "",
        "## Issues tracked",
        "",
        "| Issue | Latest kind | ok | Last ts |",
        "|-------|-------------|----|---------|",
    ]
    for issue, events in sorted(by_issue.items()):
        last = events[-1]
        lines.append(
            f"| {issue} | {last.get('kind')} | {last.get('ok')} | {last.get('ts')} |"
        )
    lines.extend(
        [
            "",
            "## Follow-up",
            "",
            "- Evidence JSONL: `docs/ops/generated/help-wanted-evidence/YYYY-MM-DD.jsonl`",
            "- This board: `docs/ops/generated/help-wanted-status.md` (+ `.json`)",
            "- Human review: read this board + open PRs linked in receipts before re-dispatching the same issue.",
            "- Dashboard (future): Vercel surface over `help-wanted-status.json` + Actions artifacts.",
            "",
            "Agent-Identity: Grok (Administrator) · help-wanted lane",
            "",
        ]
    )
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"wrote_md": str(out_md), "wrote_json": str(out_json), "receipts": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
