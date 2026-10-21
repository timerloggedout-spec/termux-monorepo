#!/usr/bin/env python3
"""Promote proposal status with lightweight tier checks."""
from __future__ import annotations
import argparse, datetime as dt, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "docs" / "proposals" / "registry.yaml"
ACTIVE = ROOT / "docs" / "proposals" / "active"
CLOSED = ROOT / "docs" / "proposals" / "closed"
ORDER = ["draft", "posted", "in_review", "accepted", "executing", "closed"]

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")

def set_registry_status(pid: str, new_status: str) -> None:
    text = load_text(REG)
    pattern = re.compile(rf"(  - id: {re.escape(pid)}\n(?:    .*\n)*?    status: )(\w+)", re.MULTILINE)
    if not pattern.search(text):
        raise SystemExit(f"FAIL: id {pid} not found in registry.yaml")
    text = pattern.sub(rf"\g<1>{new_status}", text, count=1)
    today = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    text = re.sub(r'updated_at: ".*?"', f'updated_at: "{today}"', text, count=1)
    write_text(REG, text)

def set_manifest_status(pid: str, new_status: str, evidence: str) -> None:
    man = ACTIVE / pid / "MANIFEST.md"
    if not man.exists():
        raise SystemExit(f"FAIL: missing {man}")
    text = load_text(man)
    text = re.sub(r"(?m)^status: \w+", f"status: {new_status}", text, count=1)
    stamp = dt.date.today().isoformat()
    entry = (
        f"\n### {stamp} — promote_proposal.py\n\n"
        f"- Disposition: status → **{new_status}**\n"
        f"- Notes: {evidence or '(no evidence string)'}\n"
    )
    if "## Review log" in text and "## Checklist" in text:
        text = text.replace("## Checklist", entry + "\n## Checklist", 1)
    else:
        text = text.rstrip() + "\n" + entry
    write_text(man, text)

def maybe_close_move(pid: str) -> None:
    src, dst = ACTIVE / pid, CLOSED / pid
    CLOSED.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        raise SystemExit(f"FAIL: {dst} already exists")
    src.rename(dst)
    text = load_text(REG)
    text = re.sub(
        rf"(  - id: {re.escape(pid)}\n(?:    .*\n)*?    path: )active/{re.escape(pid)}/",
        rf"\g<1>closed/{pid}/",
        text,
        count=1,
    )
    write_text(REG, text)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--to", required=True)
    ap.add_argument("--evidence", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--close-move", action="store_true")
    args = ap.parse_args()
    new = args.to
    if new not in ORDER and new != "blocked":
        print(f"FAIL: unknown status {new}", file=sys.stderr)
        return 2
    reg = load_text(REG)
    m = re.search(rf"  - id: {re.escape(args.id)}\n(?:    .*\n)*?    status: (\w+)", reg)
    if not m:
        print(f"FAIL: {args.id} not in registry", file=sys.stderr)
        return 2
    cur = m.group(1)
    if not args.force and new != "blocked" and cur in ORDER and new in ORDER:
        if ORDER.index(new) < ORDER.index(cur):
            print(f"FAIL: refuse downgrade {cur} → {new} (use --force)", file=sys.stderr)
            return 1
    if new == "accepted" and not args.evidence and not args.force:
        print("FAIL: --to accepted requires --evidence (Tier 2–3)", file=sys.stderr)
        return 1
    set_registry_status(args.id, new)
    if (ACTIVE / args.id).exists():
        set_manifest_status(args.id, new, args.evidence)
    if new == "closed" and args.close_move:
        maybe_close_move(args.id)
    print(f"OK: {args.id} {cur} → {new}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
