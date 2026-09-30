#!/usr/bin/env python3
"""Shannon-entropy scanner for staged files."""
import math, re, sys
from collections import Counter
from pathlib import Path

THRESHOLD = 4.5
MIN_LEN = 20
CAND = re.compile(r"[A-Za-z0-9+/=_\-]{%d,}" % MIN_LEN)

def shannon(s: str) -> float:
    if not s:
        return 0.0
    c = Counter(s)
    n = len(s)
    return -sum((v / n) * math.log2(v / n) for v in c.values())

def scan(path: Path) -> int:
    try:
        txt = path.read_text(errors="replace")
    except Exception:
        return 0
    hits = 0
    for m in CAND.finditer(txt):
        ent = shannon(m.group(0))
        if ent >= THRESHOLD:
            line = txt[:m.start()].count("\n") + 1
            print("  %s:%d  entropy=%.2f  len=%d" % (path, line, ent, len(m.group(0))))
            hits += 1
    return hits

if __name__ == "__main__":
    total = sum(scan(Path(p)) for p in sys.argv[1:])
    sys.exit(1 if total else 0)
