#!/usr/bin/env python3
"""Emit nc-1 interface unit records from scorer run outputs.

Interface (DoE Expert, experiment owner, 2026-10-31): per output unit
  {unit_id, surface, source_ref, layer, prose_ratio_inputs,
   layer_verdict{drift, borderline, score}, tokens_scanned}
Layers stay separable: every record carries exactly one layer tag
(L3 = GitHub surfaces, L2 = chat transcripts); the FULL arm's L1
relay-validation is applied downstream by the evaluator, never here.
drift := verdict == prose (score < 0.40); borderline (0.40..0.55) is
carried as its own flag so the evaluator can apply the corpus-set tau.
tokens_scanned := word count of the unit (documented proxy; the
evaluator can recompute exactly from source_ref).
"""
import json
import sys

BASE = "/home/hatch/workspace/classifier-build/notation/"


STRATUM = {"gh-comment": "github", "gh-pr-body": "github",
           "gh-control": "github", "chat": "chat"}


def unit(uid, surface, ref, layer, r):
    return {
        "unit_id": uid,
        "surface": surface,
        "stratum": STRATUM[surface],
        "source_ref": ref,
        "layer": layer,
        "density": r.get("density", round((r["sym_per_100w"] + r["ev_per_100w"]) / 100.0, 4)),
        "prose_ratio_inputs": {
            "sym_per_100w": r["sym_per_100w"],
            "glue_per_sent": r["glue_per_sent"],
            "mean_sent_words": r["mean_sent_words"],
            "ev_per_100w": r["ev_per_100w"],
        },
        "layer_verdict": {
            "drift": r["verdict"] == "prose",
            "borderline": r["verdict"] == "borderline",
            "score": r["score"],
        },
        "tokens_scanned": r["words"],
    }


def main() -> int:
    out = []
    l3 = json.load(open(BASE + "l3-results2.json"))
    for name, r in l3["exemplars"]:
        cid = name.rsplit(" ", 1)[-1]
        out.append(unit(f"l3-comment-{cid}", "gh-comment",
                        f"issue #1884 comment {cid}", "L3", r))
    for name, r in l3["controls"]:
        out.append(unit(f"l3-control-{abs(hash(name)) % 10**8}", "gh-control",
                        name, "L3", r))
    l3b = json.load(open(BASE + "l3-results.json"))
    for name, r in l3b["prbodies"]:
        num = name.split(" ")[1]
        out.append(unit(f"l3-prbody-{num}", "gh-pr-body",
                        f"PR {num} body", "L3", r))
    l2 = json.load(open(BASE + "l2-results.json"))
    texts = json.load(open(BASE + "l2-texts.json"))
    sys.path.insert(0, BASE)
    from compliance_scorer import score
    for row in l2:
        for i, t in enumerate(texts[row["chat"]]):
            r = score(t)
            out.append(unit(f"l2-{row['chat']}-{i}", "chat",
                            f"side-chat {row['chat']} recent turn {i}", "L2", r))
    path = BASE + "nc1-units.jsonl"
    with open(path, "w") as fh:
        for u in out:
            fh.write(json.dumps(u) + "\n")
    l3n = sum(1 for u in out if u["layer"] == "L3")
    l2n = sum(1 for u in out if u["layer"] == "L2")
    drift = sum(1 for u in out if u["layer_verdict"]["drift"])
    print(f"units={len(out)} L3={l3n} L2={l2n} drift={drift} -> {path}")
    print(json.dumps(out[0], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
