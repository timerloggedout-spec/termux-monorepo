#!/usr/bin/env python3
"""Challenge countdowns dashboard feed collector.

Contract: docs/ops/CHALLENGE-COUNTDOWNS-FEED.md. Reads the deadline
instants stored per entry in docs/ops/CHALLENGE-ENTRIES-LOG.md (the
SSOT, parsed by the challenge lane's scripts/challenge_entries/
countdowns.py) and writes apps/help-wanted-dashboard/data/
challenge-countdowns-feed.json.

The feed carries INSTANTS ONLY — never a computed state and never a
remaining-seconds value. The dashboard page derives state and
time-remaining client-side from the instants on every tick
(issue #1880 requirement 3), so a stale feed can never show a stale
countdown; at worst it shows a stale deadline, which the log owns.
"""
import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "challenge-countdowns-feed/v1"
LOG_REL = "docs/ops/CHALLENGE-ENTRIES-LOG.md"
EMITTER_REL = "scripts/challenge_entries/countdowns.py"
STATUS_WORDS = ("COMPLETED", "CLOSED", "IN PROGRESS", "REGISTERING",
                "BLOCKED", "IN REVIEW", "PENDING")


def load_emitter(root):
    spec = importlib.util.spec_from_file_location(
        "challenge_countdowns", root / EMITTER_REL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def display_title(header_rest):
    """'for C1, Workshop to Ship — IN PROGRESS (note)' -> 'for C1, Workshop to Ship'."""
    rest = header_rest.strip().lstrip("—").strip()
    parts = [p.strip() for p in rest.split(" — ")]
    keep = []
    for p in parts:
        core = re.sub(r"\s*\(.*\)\s*$", "", p).strip().upper()
        if core in STATUS_WORDS or any(core.startswith(w) for w in STATUS_WORDS):
            break
        keep.append(p)
    return " — ".join(keep) if keep else header_rest.strip()


def build_feed(root):
    mod = load_emitter(root)
    text = (root / LOG_REL).read_text(encoding="utf-8")
    titles = {}
    for m in mod.HEADER_RE.finditer(text):
        titles[m.group(1)] = display_title(m.group(2))
    entries = []
    for e in mod.parse_entries(text):
        status = (e["status"] or "").strip().upper()
        entries.append({
            "id": e["id"],
            "title": titles.get(e["id"], e["id"]),
            "status": status if status else "ACTIVE",
            "opens": e["opens"].isoformat() if e["opens"] else None,
            "closes": e["closes"].isoformat() if e["closes"] else None,
        })
    entries.sort(key=lambda e: int(e["id"][1:]))
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": LOG_REL,
        "entries": entries,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    feed = build_feed(Path(args.root))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(feed['entries'])} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
