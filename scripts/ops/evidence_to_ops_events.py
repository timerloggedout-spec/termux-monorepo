#!/usr/bin/env python3
"""
Convert help-wanted / help-given receipts into OpsEvent / Gource streams via SeekLog.

Sources:
  - evidence JSONL (docs/ops/generated/help-wanted-evidence/*.jsonl)
  - status board (docs/ops/generated/help-wanted-status.json) tributes + foreign opens

Usage:
  python3 scripts/ops/evidence_to_ops_events.py docs/ops/generated/help-wanted-evidence/*.jsonl
  python3 scripts/ops/evidence_to_ops_events.py --status docs/ops/generated/help-wanted-status.json --format summary
  python3 scripts/ops/evidence_to_ops_events.py --format gource path.jsonl
  python3 scripts/ops/evidence_to_ops_events.py --format jsonl --slice 0.7:1.0 path.jsonl

BIUDL / adaptive-wait: stdlib only. No paid credits. Dual-gate friendly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from ops_event_seeklog import OpsEvent, SeekLog  # noqa: E402

KNOWN_KINDS = {
    "upstream_pr",
    "claim",
    "claim_skipped_closed",
    "fallback",
    "notice",
    "scout_bench",
    "followup_skip_idempotent",
    "followup_skip_cooldown",
    "followup_changes_requested",
    "followup_reengage",
    "followup_stale_nudge",
    "rerequest",
    "llm_assist",
    "tribute",
    "foreign_open",
}


def _colour_for(ok: Any, kind: str) -> str:
    if ok is True:
        return "00FF00"
    if ok is False:
        return "FF0000"
    if kind.startswith("followup"):
        return "FFAA00"
    if kind in ("tribute", "upstream_pr"):
        return "4488FF"
    if kind in ("foreign_open", "claim"):
        return "66CCFF"
    return "AAAAAA"


def receipt_to_event(r: Dict[str, Any]) -> Optional[OpsEvent]:
    if not isinstance(r, dict):
        return None
    kind = str(r.get("kind") or "unknown")
    ok = r.get("ok")
    if ok is True:
        op, status = "A", "passed"
    elif ok is False:
        op, status = "D", "failed"
    else:
        op, status = "M", "observed"

    issue = r.get("issue") or r.get("pr_url") or r.get("source_id") or "unknown"
    issue_s = str(issue).replace("https://github.com/", "").replace("http://github.com/", "")
    path = f"help-given/{kind}/{issue_s}"[:160]
    actor = str(r.get("scout") or r.get("lane") or r.get("actor") or "help-wanted")
    ts = r.get("ts") or r.get("observed_at") or r.get("event_at") or r.get("last_ts") or "0"
    return OpsEvent(
        ts=ts,
        actor=actor,
        op=op,
        path=path,
        colour=_colour_for(ok, kind),
        lane=str(r.get("lane") or "help-wanted"),
        status=status,
        confidence=1.0 if ok is True else (0.0 if ok is False else 0.5),
        meta={
            k: r.get(k)
            for k in (
                "kind", "delivery", "foreign", "note", "pr_url", "run_url",
                "comment_url", "score", "title", "state", "repo",
            )
            if r.get(k) is not None
        },
    )


def tributes_to_receipts(status: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for t in status.get("tributes") or []:
        if not isinstance(t, dict):
            continue
        out.append({
            "ts": t.get("last_ts") or status.get("generated_at") or "0",
            "kind": "tribute",
            "issue": t.get("pr_url") or f"{t.get('repo')}#{t.get('number')}",
            "ok": t.get("ok", True),
            "pr_url": t.get("pr_url"),
            "lane": "help-wanted",
            "scout": "oversight",
            "title": t.get("title"),
            "state": t.get("state"),
            "repo": t.get("repo"),
            "note": f"kinds={t.get('kinds')}",
        })
    for f in status.get("foreign_open_prs") or []:
        if not isinstance(f, dict):
            continue
        out.append({
            "ts": f.get("updated_at") or status.get("generated_at") or "0",
            "kind": "foreign_open",
            "issue": f.get("html_url") or f"{f.get('repo')}#{f.get('number')}",
            "ok": True,
            "pr_url": f.get("html_url"),
            "lane": "help-wanted",
            "scout": "oversight",
            "title": f.get("title"),
            "state": f.get("state"),
            "repo": f.get("repo"),
            "foreign": True,
        })
    return out


def load_receipts(paths: Iterable[Path]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix == ".json" and text.lstrip().startswith("{"):
            try:
                obj = json.loads(text)
                if isinstance(obj, list):
                    out.extend(x for x in obj if isinstance(x, dict))
                elif isinstance(obj, dict):
                    if "tributes" in obj or "foreign_open_prs" in obj:
                        out.extend(tributes_to_receipts(obj))
                    if "receipts" in obj and isinstance(obj["receipts"], list):
                        out.extend(x for x in obj["receipts"] if isinstance(x, dict))
                    elif "ts" in obj or "kind" in obj:
                        out.append(obj)
            except json.JSONDecodeError:
                continue
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    return out


def build_log(receipts: List[Dict[str, Any]]) -> SeekLog:
    events: List[OpsEvent] = []
    for r in receipts:
        ev = receipt_to_event(r)
        if ev:
            events.append(ev)
    events.sort(key=lambda e: str(e.ts))
    return SeekLog(events)


def summarize(log: SeekLog) -> Dict[str, Any]:
    by_kind: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    by_repo: Dict[str, int] = {}
    paths: Dict[str, int] = {}
    for ev in log._events:
        kind = (ev.meta or {}).get("kind") or "unknown"
        by_kind[str(kind)] = by_kind.get(str(kind), 0) + 1
        st = ev.status or "unknown"
        by_status[st] = by_status.get(st, 0) + 1
        paths[ev.path] = paths.get(ev.path, 0) + 1
        repo = (ev.meta or {}).get("repo")
        if repo:
            by_repo[str(repo)] = by_repo.get(str(repo), 0) + 1
    saturated = sorted(((p, n) for p, n in paths.items() if n >= 5), key=lambda x: -x[1])
    return {
        "events": len(log),
        "by_kind": by_kind,
        "by_status": by_status,
        "by_repo": dict(sorted(by_repo.items(), key=lambda x: -x[1])[:20]),
        "saturated_paths": [{"path": p, "count": n} for p, n in saturated[:20]],
        "known_kinds_coverage": sorted(k for k in by_kind if k in KNOWN_KINDS),
        "unknown_kinds": sorted(k for k in by_kind if k not in KNOWN_KINDS),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Help-given evidence → OpsEvent / Gource SeekLog")
    ap.add_argument("paths", nargs="*", type=Path, help="JSONL/JSON receipt files")
    ap.add_argument("--status", type=Path, default=None, help="help-wanted-status.json")
    ap.add_argument("--format", choices=("gource", "jsonl", "summary"), default="summary")
    ap.add_argument("--slice", default=None, help="Percent slice start:stop e.g. 0.7:1.0")
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args(argv)

    paths = list(args.paths or [])
    if args.status:
        paths.append(args.status)
    if not paths:
        print("need paths and/or --status", file=sys.stderr)
        return 2
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"missing: {missing}", file=sys.stderr)
        return 2

    log = build_log(load_receipts(paths))
    if args.slice:
        a, _, b = args.slice.partition(":")
        log = log.slice(float(a or 0.0), float(b or 1.0))

    if args.format == "gource":
        body = log.to_gource_log()
    elif args.format == "jsonl":
        body = log.to_jsonl()
    else:
        body = json.dumps(summarize(log), indent=2) + "\n"

    if args.output:
        args.output.write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
