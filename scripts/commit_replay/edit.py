#!/usr/bin/env python3
"""Commit Replay — P4 edit(): surgical ops on a RECIPE, never on bytes.

[MUSEai]@{role:{commit-replay}} — edit() transforms one grecipe into the
next. Source files are never touched: an edit swaps / drops / reorders /
inserts / customizes POINTER segments and literal glue. The edited recipe
is a new version whose `lineage` records {parent_recipe_sha256, ops} —
recipe history is a hash chain of recipe files; committed recipes live in
ops/commit-replay/recipes/ and ride git's DAG like everything else.

Ops (DESIGN §2 vocabulary; applied sequentially, indices refer to the
segment list as it stands at that op):
  replace   {op, segment: i, with: <segment>}
  drop      {op, segment: i}
  reorder   {op, order: [i, j, ...]}        (permutation of current list)
  insert    {op, at: "before"|"after", segment: i, with: <segment>}
  customize {op, segment: i, set: {field: value, ...}}  (pointer fields:
             start_line/end_line/symbol/path — retarget or narrow a range)

Usage: edit.py --recipe in.json --ops ops.json [--out out.json]
ops.json = {"ops": [ ... ]} or a bare list.
"""
import argparse, hashlib, json, sys


def apply_ops(recipe, ops):
    segs = list(recipe["segments"])
    report = []
    for k, op in enumerate(ops):
        kind = op["op"]
        if kind == "replace":
            segs[op["segment"]] = op["with"]
        elif kind == "drop":
            segs.pop(op["segment"])
        elif kind == "reorder":
            assert sorted(op["order"]) == list(range(len(segs))), \
                "reorder must be a permutation"
            segs = [segs[i] for i in op["order"]]
        elif kind == "insert":
            at = op["segment"] + (1 if op.get("at") == "after" else 0)
            segs.insert(at, op["with"])
        elif kind == "customize":
            seg = dict(segs[op["segment"]])
            assert "literal" not in seg, "customize targets pointers"
            seg.update(op["set"])
            segs[op["segment"]] = seg
        else:
            raise ValueError(f"unknown op: {kind}")
        report.append({"step": k, "op": kind,
                       "segments_after": len(segs)})
    out = dict(recipe)
    out["segments"] = segs
    return out, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipe", required=True)
    ap.add_argument("--ops", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    raw = open(a.recipe, "rb").read()
    recipe = json.loads(raw)
    ops_doc = json.load(open(a.ops, encoding="utf-8"))
    ops = ops_doc["ops"] if isinstance(ops_doc, dict) else ops_doc
    edited, report = apply_ops(recipe, ops)
    lineage = list(edited.get("lineage", []))
    lineage.append({"parent_recipe_sha256":
                    hashlib.sha256(raw).hexdigest(), "ops": ops})
    edited["lineage"] = lineage
    out = a.out or a.recipe
    with open(out, "w", encoding="utf-8") as f:
        json.dump(edited, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"edited_recipe": out, "report": report,
                      "lineage_depth": len(lineage)},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
