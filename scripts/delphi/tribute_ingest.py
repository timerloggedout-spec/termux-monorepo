"""Collect Tribute System 1 delphi_signal outcomes for the Delphi gate (no network, stdlib only).

  python3 -m scripts.delphi.tribute_ingest decisions.jsonl [more.jsonl ...]
Reads tribute_system1 decision rows, keeps each row's delphi_signal, keys it by the thread url
(the gate dedupes on key+outcome, so re-scans and overlapping backfills are idempotent), and
writes `signal` (compact JSON array, <= 200, newest file first) and `n` to $GITHUB_OUTPUT.
"""
from __future__ import annotations

import json, os, sys

from scripts.delphi.gate import MAX_SIGNALS


def collect(paths: list[str], cap: int = MAX_SIGNALS) -> list[dict]:
    out, seen = [], set()
    for path in sorted(paths, reverse=True):  # backfill/YYYY-MM-DD.jsonl: newest day first
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            sg = row.get("delphi_signal") if isinstance(row, dict) else None
            if not isinstance(sg, dict) or "weight" not in sg:
                continue
            key = str((row.get("subject") or {}).get("url") or "")
            ident = (key, sg.get("outcome"))
            if key and ident in seen:
                continue
            seen.add(ident)
            item = {k: sg.get(k) for k in ("surface", "repo", "outcome", "weight")}
            if key:
                item["key"] = key
            out.append(item)
            if len(out) >= cap:
                return out
    return out


def main(argv=None) -> int:
    paths = list(argv if argv is not None else sys.argv[1:])
    sigs = collect(paths)
    print(f"::notice::delphi tribute-ingest files={len(paths)} signals={len(sigs)}")
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as f:
        f.write(f"n={len(sigs)}\nsignal<<DELPHI_EOF\n{json.dumps(sigs, separators=(',', ':'))}\nDELPHI_EOF\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
