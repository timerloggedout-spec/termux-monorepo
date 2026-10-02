"""Redact PII + secrets from files with context preservation.

Preserves word boundaries + surrounding characters:
  "call +1 555-123-4567 now" -> "call [PHONE:REDACTED] now"
Usage:
    python3 redact_pii.py --dry-run <file> [<file>...]
    python3 redact_pii.py --in-place <file> [<file>...]
"""
from __future__ import annotations
import argparse, json, re, shutil, sys, time
from pathlib import Path

PATTERNS = [
    ("GH_TOKEN",    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("GH_PAT",      re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("OPENAI_SK",   re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("ANTHROPIC",   re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("GOOGLE_AIZA", re.compile(r"AIza[0-9A-Za-z_\-]{20,}")),
    ("HINDSIGHT",   re.compile(r"hsk_[a-z0-9_]{20,}")),
    ("AWS_AKIA",    re.compile(r"AKIA[0-9A-Z]{16}")),
    ("SLACK",       re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}")),
    ("EMAIL",       re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    ("PHONE_US",    re.compile(r"(?:\+1[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}\b")),
    ("SSN",         re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("PASSWORD_KV", re.compile(r"(?i)\bpassword\s*[:=]\s*['\"]?[^\s'\"]{6,}")),
    ("BEARER",      re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}")),
]

def redact(text: str) -> tuple[str, dict]:
    hits = {}
    for name, pat in PATTERNS:
        def _sub(m):
            hits[name] = hits.get(name, 0) + 1
            return "[" + name + ":REDACTED]"
        text = pat.sub(_sub, text)
    return text, hits

def process(path: Path, in_place: bool, dry_run: bool):
    if not path.is_file():
        print("  skip: " + str(path)); return
    src = path.read_text(errors="replace")
    out, hits = redact(src)
    if not hits:
        print("  clean: " + str(path)); return
    if dry_run:
        print("  would redact " + str(path) + ": " + json.dumps(hits))
        return
    if in_place:
        bak = path.with_suffix(path.suffix + ".bak." + str(int(time.time())))
        shutil.copy2(path, bak)
        path.write_text(out)
        print("  redacted " + str(path) + " (backup " + bak.name + ")")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()
    if not args.dry_run and not args.in_place:
        ap.error("choose --dry-run or --in-place")
    total = 0
    for f in args.files:
        for p in Path(".").rglob(f) if ("*" in f or "?" in f) else [Path(f)]:
            process(p, args.in_place, args.dry_run)
            total += 1
    print("  files: " + str(total))

if __name__ == "__main__":
    main()
