"""Scripted <3-minute demo for StudySprint (D1).

Three requests, offline, against the sample syllabus in examples/:
1. asserted-only -> ABSTAIN (a claimed syllabus is not evidence)
2. fetched syllabus -> ALLOW_RECOMMENDATION + plan + week-1 quiz +
   re-plan carrying week 1 into week 2
3. credential_mutation -> ESCALATE even with material evidence

Writes evidence/demo-run.json. Run: python3 demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from agent import run_agent

SCENARIOS = [
    {"id": "no-evidence", "action": "draft", "asserted": True,
     "narration": "Plan my BIO 101 study — the student asserts the "
                  "course topics, no syllabus file named."},
    {"id": "fetched-syllabus", "action": "draft", "asserted": True,
     "artifact": {"kind": "syllabus", "ref": "examples/syllabus.json"},
     "missed_week": 1,
     "narration": "Same request, syllabus file named: fetch_study_"
                  "evidence stamps it, the gate allows, the plan + "
                  "quiz are built, and missed week 1 is re-planned."},
    {"id": "credential", "action": "credential_mutation",
     "risk_tier": "consequential", "asserted": True,
     "artifact": {"kind": "syllabus", "ref": "examples/syllabus.json"},
     "narration": "A credential-mutation request with fetched, "
                  "material evidence — the class rule still escalates."},
]


def main() -> None:
    out = {"demo": "studysprint", "scenarios": []}
    for s in SCENARIOS:
        request = {k: s[k] for k in ("id", "action", "risk_tier",
                                     "asserted", "artifact", "missed_week")
                   if k in s}
        receipt = run_agent(request)
        print(f"[{s['id']}] {s['narration']}")
        print(f"  asserted -> {receipt['decision_on_asserted_evidence']}"
              f" | final -> {receipt['decision_final']}"
              f" | plan sessions: "
              f"{receipt['plan']['total_sessions'] if receipt['plan'] else 0}")
        out["scenarios"].append({"narration": s["narration"],
                                 "receipt": receipt})
    target = Path(__file__).parent / "evidence" / "demo-run.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nrun evidence written: {target}")


if __name__ == "__main__":
    main()
