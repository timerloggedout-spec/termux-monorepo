#!/usr/bin/env python3
"""Append a structured VOTE block to a proposal DEBATE.md."""
from __future__ import annotations
import argparse, datetime as dt, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ACTIVE = ROOT / "docs" / "proposals" / "active"
ALLOWED = {"accept", "reject", "abstain", "summary OK"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposal", required=True)
    ap.add_argument("--term", required=True)
    ap.add_argument("--voter", required=True)
    ap.add_argument("--vote", required=True, choices=sorted(ALLOWED))
    ap.add_argument("--reason", default="")
    ap.add_argument("--at", default=dt.date.today().isoformat())
    args = ap.parse_args()
    debate = ACTIVE / args.proposal / "DEBATE.md"
    if not debate.exists():
        print(f"FAIL: no DEBATE.md at {debate}", file=sys.stderr)
        return 2
    block = (
        f"\n### {args.at} — {args.voter}\n\n"
        f"```text\nVOTE: {args.vote}\nvoter: {args.voter}\n"
        f"term: {args.term}\nat: {args.at}\nreason: {args.reason}\n```\n"
    )
    text = debate.read_text(encoding="utf-8")
    marker = "## Votes"
    if marker not in text:
        text = text.rstrip() + f"\n\n{marker}\n\n_(none yet)_\n"
    if "_(none yet)_" in text:
        text = text.replace("_(none yet)_", block.strip(), 1)
    else:
        idx = text.find(marker)
        rest = text[idx:]
        next_h = rest.find("\n## ", 1)
        if next_h == -1:
            text = text.rstrip() + "\n" + block
        else:
            abs_i = idx + next_h
            text = text[:abs_i].rstrip() + "\n" + block + text[abs_i:]
    debate.write_text(text, encoding="utf-8")
    print(f"OK: recorded VOTE:{args.vote} for {args.term}")
    print("Reminder: copy binding outcome into MANIFEST Review log.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
