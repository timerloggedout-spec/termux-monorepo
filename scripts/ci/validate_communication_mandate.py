#!/usr/bin/env python3
"""SG002: check authored directive lines for negative-form openings."""
from pathlib import Path
import re
import sys

# Quoted source text, code fences, and the policy registry itself remain verbatim.
EXEMPT_NAMES = {"COMMUNICATION-MANDATE.md"}
NEGATIVE_OPEN = re.compile(r"^\\s*(?:[-*+]\\s+)?(?:No|Not|Don't|Never)\\b", re.IGNORECASE)
DIRECTIVE = re.compile(r"^\\s*(?:[-*+]\\s+)?(?:No|Not|Don't|Never)\\b", re.IGNORECASE)

def violations(path: Path):
    if path.name in EXEMPT_NAMES or path.suffix.lower() not in {".md", ".txt"}:
        return []
    found, in_fence = [], False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith(">"):
            continue
        if DIRECTIVE.match(line):
            found.append((number, line.strip()))
    return found

def main():
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        paths = [p for p in Path(".").rglob("*.md") if ".git" not in p.parts and "node_modules" not in p.parts]
    errors = []
    for path in paths:
        if path.exists():
            errors.extend((path, n, line) for n, line in violations(path))
    if errors:
        for path, number, line in errors:
            print(f"SG002 {path}:{number}: rewrite directive as a positive DO statement: {line}", file=sys.stderr)
        return 1
    print(f"SG002 PASS: {len(paths)} authored text paths inspected")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
