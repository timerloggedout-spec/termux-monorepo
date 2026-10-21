#!/usr/bin/env python3
"""Eval harness for Tribute System 1 (CI check).

Reads every labeled fixture (a thread JSON with an "expected" block, or a list
of them) and reports per-class precision/recall, escalation rate, action
accuracy, and false re-engagements. Exits 1 when a gate fails:
  - any false re-engagement (we would comment after a decline/claim/close)
  - any seed case (non-synthetic) with the wrong primary label or action
  - macro precision or recall below --min-precision / --min-recall
Writes a markdown report for $GITHUB_STEP_SUMMARY with --summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from scripts.ci import tribute_system1 as s1
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.ci import tribute_system1 as s1  # type: ignore

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "tribute_system1"


def load_cases(paths: list[Path]) -> list[dict]:
    out = []
    for p in paths:
        files = sorted(p.glob("*.json")) if p.is_dir() else [p]
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            for case in data if isinstance(data, list) else [data]:
                if isinstance(case, dict) and "expected" in case:
                    out.append(case)
    return out


def evaluate(cases: list[dict]) -> dict:
    tp = {l: 0 for l in s1.LABELS}; fp = dict(tp); fn = dict(tp)
    rows, false_reengage, escalated, action_ok, seed_fail = [], [], 0, 0, []
    for c in cases:
        d = s1.route(c)
        exp = c["expected"]
        pred = {l["label"] for l in d["labels"] if l["confidence"] >= s1.CONFIDENT}
        want = set(exp.get("labels") or [])
        for l in s1.LABELS:
            tp[l] += l in pred and l in want
            fp[l] += l in pred and l not in want
            fn[l] += l in want and l not in pred
        escalated += d["escalate"]
        ok = d["primary"] == exp.get("primary") and d["action"] == exp.get("action")
        action_ok += ok
        if d["reengage_allowed"] and exp.get("reengage_allowed") is False:
            false_reengage.append(c["case_id"])
        if not c.get("synthetic") and not ok:
            seed_fail.append(c["case_id"])
        rows.append({"case": c["case_id"], "synthetic": bool(c.get("synthetic")), "primary": d["primary"],
                     "expected": exp.get("primary"), "action": d["action"], "rung": d["rung"], "ok": ok,
                     "labels": {l["label"]: l["confidence"] for l in d["labels"]}})
    per = {}
    for l in s1.LABELS:
        support = tp[l] + fn[l]
        if support == 0 and fp[l] == 0:
            continue
        p = tp[l] / (tp[l] + fp[l]) if tp[l] + fp[l] else 0.0
        r = tp[l] / support if support else 0.0
        per[l] = {"precision": round(p, 3), "recall": round(r, 3), "support": support, "tp": tp[l], "fp": fp[l], "fn": fn[l]}
    scored = [v for v in per.values() if v["support"]]
    n = len(cases) or 1
    return {
        "cases": len(cases),
        "per_class": per,
        "macro_precision": round(sum(v["precision"] for v in scored) / len(scored), 3) if scored else 0.0,
        "macro_recall": round(sum(v["recall"] for v in scored) / len(scored), 3) if scored else 0.0,
        "action_accuracy": round(action_ok / n, 3),
        "escalation_rate": round(escalated / n, 3),
        "false_reengage": false_reengage,
        "seed_failures": seed_fail,
        "rows": rows,
    }


def markdown(r: dict) -> str:
    out = ["## Tribute System 1 eval", "",
           f"cases **{r['cases']}** · action accuracy **{r['action_accuracy']}** · escalation rate **{r['escalation_rate']}** · "
           f"false re-engage **{len(r['false_reengage'])}** · macro P/R **{r['macro_precision']}/{r['macro_recall']}**", "",
           "| class | precision | recall | support |", "|---|---|---|---|"]
    out += [f"| {k} | {v['precision']} | {v['recall']} | {v['support']} |" for k, v in r["per_class"].items()]
    out += ["", "| case | primary | expected | action | rung | ok |", "|---|---|---|---|---|---|"]
    out += [f"| {x['case']} | {x['primary']} | {x['expected']} | {x['action']} | {x['rung']} | {'✅' if x['ok'] else '❌'} |" for x in r["rows"]]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--min-precision", type=float, default=0.9)
    ap.add_argument("--min-recall", type=float, default=0.9)
    ap.add_argument("--json", default="")
    ap.add_argument("--summary", default="")
    a = ap.parse_args(argv)
    r = evaluate(load_cases(a.paths or [DEFAULT_DIR]))
    md = markdown(r)
    print(md)
    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=1), encoding="utf-8")
    if a.summary:
        with open(a.summary, "a", encoding="utf-8") as fh:
            fh.write(md)
    gates = []
    if r["false_reengage"]:
        gates.append(f"false re-engagements: {r['false_reengage']}")
    if r["seed_failures"]:
        gates.append(f"seed cases misrouted: {r['seed_failures']}")
    if r["macro_precision"] < a.min_precision or r["macro_recall"] < a.min_recall:
        gates.append(f"macro P/R {r['macro_precision']}/{r['macro_recall']} below {a.min_precision}/{a.min_recall}")
    for g in gates:
        print(f"::error::tribute-system1 eval gate: {g}")
    return 1 if gates else 0


if __name__ == "__main__":
    raise SystemExit(main())
