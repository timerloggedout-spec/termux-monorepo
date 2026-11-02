#!/usr/bin/env python3
"""Commit Replay — P3 jit_resolve (commit-store/v1).

[MUSEai]@{role:{commit-replay}} — just-in-time resolution: a recipe may
name fragments by SYMBOL only ({"symbol": "parse_commit"} or
{"symbol": "iso", "path": "scripts/..."}) — the author pays tokens for
names, not content. jit_resolve looks each symbol up in the fragment
index and fills the full gpointer {path, blob, symbol, start_line,
end_line}. Deterministic pick: path filter if given, else candidates
sorted by (path, start_line), first wins; candidate counts are reported
(ambiguity is visible, never silent). Lazy: resolution touches only the
index; blob bytes are fetched later, only by compose(), only for the
segments actually materialized.

Usage:
  jit.py --fragments frag.jsonl --symbol NAME [--symbol NAME...]
  jit.py --fragments frag.jsonl --recipe in.json [--out resolved.json]
"""
import argparse, json, sys


def load_index(path):
    idx, header = {}, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("kind") == "header":
                header = r
            elif "symbol" in r:
                idx.setdefault(r["symbol"], []).append(r)
    for v in idx.values():
        v.sort(key=lambda r: (r["path"], r["start_line"]))
    return idx, header


def resolve_one(idx, seg):
    sym = seg["symbol"]
    cands = idx.get(sym, [])
    if seg.get("path"):
        cands = [c for c in cands if c["path"] == seg["path"]]
    if not cands:
        return None, 0
    c = cands[0]
    out = dict(seg)
    out.update({"path": c["path"], "blob": c["blob"],
                "start_line": c["start_line"],
                "end_line": c["end_line"]})
    return out, len(idx.get(sym, []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fragments", required=True)
    ap.add_argument("--symbol", action="append", default=[])
    ap.add_argument("--recipe")
    ap.add_argument("--out")
    a = ap.parse_args()
    idx, _hdr = load_index(a.fragments)

    if a.symbol:
        res, missing = {}, []
        for sym in a.symbol:
            ptr, n = resolve_one(idx, {"symbol": sym})
            if ptr is None:
                missing.append(sym)
            else:
                res[sym] = {**ptr, "candidates": n}
        print(json.dumps({"resolved": res, "missing": missing},
                         indent=1, sort_keys=True))
        return 1 if missing else 0

    if a.recipe:
        recipe = json.load(open(a.recipe, encoding="utf-8"))
        report = []
        for i, seg in enumerate(recipe["segments"]):
            if "literal" in seg or "blob" in seg:
                continue  # glue / already-resolved pointer: passthrough
            ptr, n = resolve_one(idx, seg)
            if ptr is None:
                print(json.dumps({"error": "unresolved symbol",
                                  "segment": i, "symbol": seg.get("symbol")}))
                return 1
            recipe["segments"][i] = ptr
            report.append({"segment": i, "symbol": ptr["symbol"],
                           "path": ptr["path"], "candidates": n})
        out = a.out or a.recipe
        with open(out, "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=1, sort_keys=True)
            f.write("\n")
        print(json.dumps({"resolved_recipe": out, "report": report},
                         indent=1, sort_keys=True))
        return 0

    ap.error("one of --symbol/--recipe required")


if __name__ == "__main__":
    sys.exit(main())
