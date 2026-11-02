#!/usr/bin/env python3
"""Rate-limit event audit gate (owner standard 2026-11-01: the events
register gets AUDITED into improvements). State-gated by construction:
this checker compares the events register against the audits record
and reports FIRE when register events exist that no audit finding
covers - it runs on register growth (push on the events file), never
on a clock. The audit itself (classification + improvements) is
authored by the quota-specialist lane into
ops/quota/rate-limit-event-audits.json; this script is the trigger
and the coverage proof, not the auditor.

Exit 0 = every register event is covered by >=1 finding.
Exit 1 = unaudited events exist (audit owed) or records are malformed.

Usage: python3 scripts/quota_event_audit.py [--root .]
"""
import argparse
import json
import sys
from pathlib import Path


def load(root, rel):
    p = Path(root) / rel
    return json.loads(p.read_text()) if p.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    a = ap.parse_args()

    reg = load(a.root, "ops/quota/rate-limit-events.json")
    aud = load(a.root, "ops/quota/rate-limit-event-audits.json")
    if reg is None or aud is None:
        print("FAIL records missing (register or audits)")
        return 1
    events = reg.get("events", [])
    ids = [e.get("id") for e in events]
    if len(ids) != len(set(ids)):
        print("FAIL register carries duplicate event ids")
        return 1
    covered = set()
    findings = 0
    for entry in aud.get("audits", []):
        for f in entry.get("findings", []):
            findings += 1
            for ref in f.get("event_refs", []):
                covered.add(ref)
    unaudited = [i for i in ids if i not in covered]
    dangling = [c for c in covered if c not in set(ids)]
    print(f"register events: {len(ids)} | audits: "
          f"{len(aud.get('audits', []))} | findings: {findings} | "
          f"covered: {len(covered & set(ids))} | unaudited: "
          f"{len(unaudited)}")
    for i in unaudited:
        print(f"UNAUDITED {i}")
    for d in dangling:
        print(f"DANGLING finding ref (no such event): {d}")
    fire = bool(unaudited or dangling)
    print(f"audit-fire={'true' if unaudited else 'false'} "
          f"verdict={'FAIL' if fire else 'PASS'}")
    try:
        import os
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as fh:
                fh.write(f"fire={'true' if unaudited else 'false'}\n")
    except OSError:
        pass
    return 1 if fire else 0


if __name__ == "__main__":
    sys.exit(main())
