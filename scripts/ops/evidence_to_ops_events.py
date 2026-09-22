#!/usr/bin/env python3
"""
Convert help-wanted evidence JSONL (and similar receipts) into OpsEvent /
Gource custom-log streams via SeekLog.

Usage:
  python3 scripts/ops/evidence_to_ops_events.py docs/ops/generated/help-wanted-evidence/*.jsonl
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

# Allow running from repo root or scripts/ops
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from ops_event_seeklog import OpsEvent, SeekLog  # noqa: E402


def receipt_to_event(r: Dict[str, Any]) -> Optional[OpsEvent]:
    """Map a help-wanted evidence receipt (or compatible dict) to OpsEvent."""
    if not isinstance(r, dict):
        return None
    kind = str(r.get("kind") or "unknown")
    ok = r.get("ok")
    if ok is True:
        op, status, colour = "A", "passed", "00FF00"
    elif ok is False:
        op, status, colour = "D", "failed", "FF0000"
    else:
        op, status, colour = "M", "observed", "FFAA00"

    issue = r.get("issue") or r.get("pr_url") or r.get("source_id") or "unknown"
    issue_s = str(issue).replace("https://github.com/", "").replace("http://github.com/", "")
    path = f"help-wanted/{kind}/{issue_s}"[:160]
    actor = str(r.get("scout") or r.get("lane") or "help-wanted")
    ts = r.get("ts") or r.get("observed_at") or r.get("event_at") or "0"
    return OpsEvent(
        ts=ts,
        actor=actor,
        op=op,
        path=path,
        colour=colour,
        lane=str(r.get("lane") or "help-wanted"),
        status=status,
        confidence=1.0 if ok is True else (0.0 if ok is False else 0.5),
        meta={
            k: r.get(k)
            for k in ("kind", "delivery", "foreign", "note", "pr_url", "run_url")
            if r.get(k) is not None
        },
    )


def load_receipts(paths: Iterable[Path]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines() if p.suffix in (".jsonl", ".log") or "\n{" in text else [text]
        if p.suffix == ".json" and text.lstrip().startswith("{"):
            try:
                obj = json.loads(text)
                if isinstance(obj, list):
                    out.extend(x for x in obj if isinstance(x, dict))
                elif isinstance(obj, dict):
                    if "receipts" in obj and isinstance(obj["receipts"], list):
                        out.extend(x for x in obj["receipts"] if isinstance(x, dict))
                    elif "ts" in obj or "kind" in obj:
                        out.append(obj)
            except json.JSONDecodeError:
                continue
            continue
        for line in lines:
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
    paths: Dict[str, int] = {}
    for ev in log._events:
        kind = (ev.meta or {}).get("kind") or "unknown"
        by_kind[str(kind)] = by_kind.get(str(kind), 0) + 1
        st = ev.status or "unknown"
        by_status[st] = by_status.get(st, 0) + 1
        paths[ev.path] = paths.get(ev.path, 0) + 1
    saturated = sorted(
        ((p, n) for p, n in paths.items() if n >= 5),
        key=lambda x: -x[1],
    )
    return {
        "events": len(log),
        "by_kind": by_kind,
        "by_status": by_status,
        "saturated_paths": [{"path": p, "count": n} for p, n in saturated[:20]],
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Evidence JSONL → OpsEvent / Gource SeekLog")
    ap.add_argument("paths", nargs="+", type=Path, help="JSONL/JSON receipt files")
    ap.add_argument(
        "--format",
        choices=("gource", "jsonl", "summary"),
        default="summary",
        help="Output format (default: summary)",
    )
    ap.add_argument(
        "--slice",
        default=None,
        help="Percent slice start:stop e.g. 0.7:1.0",
    )
    ap.add_argument("-o", "--output", type=Path, default=None, help="Write to file instead of stdout")
    args = ap.parse_args(argv)

    missing = [p for p in args.paths if not p.exists()]
    if missing:
        print(f"missing: {missing}", file=sys.stderr)
        return 2

    log = build_log(load_receipts(args.paths))
    if args.slice:
        a, _, b = args.slice.partition(":")
        start = float(a or 0.0)
        stop = float(b or 1.0)
        log = log.slice(start, stop)

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
