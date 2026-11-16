"""Tribute System 1 → Delphi outcome ingestion (issue #1533).

Reads Tribute System 1 decision records (JSONL, one decision per line)
and extracts each record's `delphi_signal`, keyed by the thread URL
(`subject.url`) so the gate can dedupe idempotently on key+outcome.
Stdlib only, no network: this module shapes the batch; the gate does
the ledger work.

  python3 scripts/delphi/tribute_ingest.py decisions.jsonl [more.jsonl ...]
      -> the signal array as JSON on stdout (for delphi-signal.yml)
  python3 scripts/delphi/tribute_ingest.py --summary decisions.jsonl
      -> counts / sum / mean on stderr, array still on stdout
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter


def extract(records: list[dict]) -> list[dict]:
    """One signal per record carrying a delphi_signal. The key is the
    decision's thread URL; a record without one still flows, unkeyed
    (the gate never dedupes unkeyed signals)."""
    out = []
    for rec in records:
        sig = rec.get("delphi_signal")
        if not isinstance(sig, dict):
            continue
        item = {"surface": sig.get("surface", ""),
                "repo": sig.get("repo") or "",
                "outcome": sig.get("outcome", "")}
        if isinstance(sig.get("weight"), (int, float)):
            item["weight"] = sig["weight"]
        url = (rec.get("subject") or {}).get("url")
        if isinstance(url, str) and url:
            item["key"] = url
        out.append(item)
    return out


def read_jsonl(paths: list[str]) -> list[dict]:
    records = []
    for path in paths:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tribute S1 -> Delphi signals")
    parser.add_argument("inputs", nargs="+", help="decision JSONL file(s)")
    parser.add_argument("--summary", action="store_true",
                        help="print batch counts/sum/mean to stderr")
    args = parser.parse_args(argv)
    signals = extract(read_jsonl(args.inputs))
    if args.summary:
        counts = Counter(s["outcome"] for s in signals)
        weights = [s["weight"] for s in signals if "weight" in s]
        total = round(sum(weights), 3)
        mean = round(total / len(weights), 3) if weights else 0.0
        print(f"tribute-ingest: {len(signals)} signals "
              f"({dict(counts)}); sum {total}, mean {mean}; "
              f"keyed {sum(1 for s in signals if 'key' in s)}",
              file=sys.stderr)
    json.dump(signals, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
