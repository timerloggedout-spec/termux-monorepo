#!/usr/bin/env python3
"""Hackathon countdowns — computed from the challenge log's stored instants.

Owner requirement (issue #1880): countdowns are always COMPUTED from the
deadline instants stored per entry in docs/ops/CHALLENGE-ENTRIES-LOG.md —
never hand-typed, never copied between surfaces.

Each section-4 packet stores a machine-readable line:
  <!-- countdown-data:D1 opens=2026-10-28T00:00:00-07:00 closes=2026-11-04T23:59:00-08:00 -->
('-' means no such instant.) Its visible state line:
  <!-- countdown:D1 -->...<!-- /countdown:D1 -->
is owned by this script:

  countdowns.py LOG            print the refreshed log to stdout
  countdowns.py LOG --write    rewrite the computed lines in place
  countdowns.py LOG --block    print the one-line countdown block (reports)
  countdowns.py LOG --json     emit instants+states as JSON (dashboard feed)
  --now ISO                    override 'now' (tests)

States: CLOSED (entry completed/closed), opens in Xd Xh, closes in Xd Xh,
OVERDUE (close instant passed, entry not completed).
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
DATA_RE = re.compile(
    r"<!-- countdown-data:(D\d+) opens=(\S+) closes=(\S+) -->")
LINE_RE = re.compile(
    r"(<!-- countdown:(D\d+) -->).*?(<!-- /countdown:\2 -->)")
HEADER_RE = re.compile(r"^### (D\d+) (.*)$", re.M)


def _parse_instant(raw):
    if raw == "-":
        return None
    return datetime.fromisoformat(raw)


def _fmt_dur(delta):
    total = int(delta.total_seconds())
    if total < 0:
        total = 0
    d, rem = divmod(total, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


def _fmt_instant(dt):
    return dt.astimezone(PT).strftime("%b %-d %H:%M PT")


def entry_state(now, opens, closes, status):
    if status and status.strip().upper().startswith(("COMPLETED", "CLOSED")):
        return "CLOSED"
    if opens is not None and now < opens:
        return f"opens in {_fmt_dur(opens - now)}"
    if closes is not None and now <= closes:
        return f"closes in {_fmt_dur(closes - now)}"
    if closes is not None and now > closes:
        return "OVERDUE"
    if opens is not None and now >= opens:
        return "OPEN"
    return "CLOSED"


def parse_entries(text):
    statuses = {}
    for m in HEADER_RE.finditer(text):
        rest = m.group(2).upper()
        if "COMPLETED" in rest:
            statuses[m.group(1)] = "COMPLETED"
        elif "CLOSED" in rest:
            statuses[m.group(1)] = "CLOSED"
        else:
            statuses[m.group(1)] = ""
    entries = []
    for m in DATA_RE.finditer(text):
        eid = m.group(1)
        entries.append({
            "id": eid,
            "opens": _parse_instant(m.group(2)),
            "closes": _parse_instant(m.group(3)),
            "status": statuses.get(eid, ""),
        })
    return entries


def refresh(text, now):
    entries = {e["id"]: e for e in parse_entries(text)}
    stamp = now.astimezone(PT).strftime("%Y-%m-%d %H:%M PT")

    def repl(m):
        e = entries.get(m.group(2))
        if e is None:
            return m.group(0)
        state = entry_state(now, e["opens"], e["closes"], e["status"])
        return f"{m.group(1)}⏳ {state} (computed {stamp}){m.group(3)}"

    return LINE_RE.sub(repl, text)


def block_line(entries, now):
    parts = []
    for e in entries:
        state = entry_state(now, e["opens"], e["closes"], e["status"])
        seg = f"{e['id']}: {state}"
        if e["closes"] is not None and not state.startswith(("closes", "CLOSED")):
            seg += f" (closes {_fmt_instant(e['closes'])})"
        parts.append(seg)
    return "⏳ countdowns — " + " · ".join(parts)


def as_json(entries, now):
    out = []
    for e in entries:
        out.append({
            "id": e["id"],
            "opens": e["opens"].isoformat() if e["opens"] else None,
            "closes": e["closes"].isoformat() if e["closes"] else None,
            "state": entry_state(now, e["opens"], e["closes"], e["status"]),
            "seconds_to_open": (
                int((e["opens"] - now).total_seconds()) if e["opens"] else None),
            "seconds_to_close": (
                int((e["closes"] - now).total_seconds()) if e["closes"] else None),
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--block", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--now")
    args = ap.parse_args(argv)

    now = (datetime.fromisoformat(args.now) if args.now
           else datetime.now(timezone.utc))
    with open(args.log, encoding="utf-8") as fh:
        text = fh.read()
    entries = parse_entries(text)
    if args.block:
        print(block_line(entries, now))
    elif args.json:
        print(json.dumps(as_json(entries, now), indent=2))
    else:
        out = refresh(text, now)
        if args.write:
            with open(args.log, "w", encoding="utf-8") as fh:
                fh.write(out)
        else:
            sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
