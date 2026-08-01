#!/usr/bin/env python3
"""Restore historical code blobs while redacting only high-confidence secrets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


RULES = (
    ("bearer", re.compile(r"(?i)\b(Bearer\s+)[A-Za-z0-9._~+/=-]{12,}")),
    ("github", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}")),
    ("openai", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}")),
    ("private_key", re.compile(r"(?s)-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----")),
    ("url_secret", re.compile(r"(?i)([?&](?:access_token|api_key|key|password|token)=)[^&#\s]{12,}")),
    ("assignment", re.compile(r'''(?ix)(\b(?:api[_-]?key|access[_-]?token|authorization|client[_-]?secret|cookie|password|secret|token)\b\s*[:=]\s*["']?)(?!\$\{|os\.environ|process\.env)([A-Za-z0-9._~+/=-]{16,})''')),
)


def redact(text: str) -> tuple[str, Counter[str]]:
    """Replace secret values, retaining all surrounding source text."""
    counts: Counter[str] = Counter()
    for name, pattern in RULES:
        def replacement(match: re.Match[str]) -> str:
            counts[name] += 1
            if name == "private_key":
                return "[REDACTED PRIVATE KEY]"
            if name in {"bearer", "url_secret", "assignment"}:
                return f"{match.group(1)}[REDACTED]"
            return "[REDACTED]"
        text = pattern.sub(replacement, text)
    return text, counts


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="ee18070")
    parser.add_argument("--prefix", default="cli-synthegration/codex/blobs")
    parser.add_argument("--output", type=Path, default=Path("cli-synthegration/codex/blobs"))
    parser.add_argument("--manifest", type=Path, default=Path("cli-synthegration/codex/blobs.manifest.json"))
    args = parser.parse_args()

    paths = git("ls-tree", "-r", "--name-only", args.source, "--", args.prefix).decode().splitlines()
    if not paths:
        raise SystemExit(f"No blobs found at {args.source}:{args.prefix}")
    records, totals = [], Counter()
    for source_path in paths:
        raw = git("show", f"{args.source}:{source_path}").decode("utf-8", "surrogateescape")
        clean, counts = redact(raw)
        relative = Path(source_path).relative_to(args.prefix)
        destination = args.output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(clean, encoding="utf-8", errors="surrogateescape")
        totals.update(counts)
        records.append({"id": relative.stem, "sha256": hashlib.sha256(clean.encode("utf-8", "surrogateescape")).hexdigest(), "redactions": sum(counts.values())})
    args.manifest.write_text(json.dumps({"source_revision": args.source, "blob_count": len(records), "redactions_by_rule": dict(totals), "blobs": records}, indent=2) + "\n")
    print(f"Sanitized {len(records)} blobs; applied {sum(totals.values())} redactions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
