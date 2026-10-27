"""Scripted <3-minute demo for the D0 completion record.

Three decision requests against this public repo, run live (read-only):

1. no-evidence      — a merge-readiness question with asserted evidence
                      only -> ABSTAIN (claims are not evidence).
2. fetched-evidence — the same question naming PR #1620; fetch_evidence
                      retrieves its real state + check runs -> the oracle
                      grades fetched evidence -> ALLOW_RECOMMENDATION,
                      with a versioned receipt.
3. credential       — a credential_mutation request naming a workflow
                      file; evidence is fetched and is material, and the
                      decision is still ESCALATE — the consequential class
                      rule runs before evidence is weighed.

Writes the full run to evidence/demo-run.json and prints a transcript.
Run:  python3 demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from agent import run_agent

SCENARIOS = [
    {
        "id": "no-evidence",
        "action": "inspect",
        "risk_tier": "standard",
        "asserted": True,
        "narration": "Is PR #1620 ready? The requester asserts 'checks are green' — no artifact named, nothing fetched.",
    },
    {
        "id": "fetched-evidence",
        "action": "inspect",
        "risk_tier": "standard",
        "asserted": True,
        "artifact": {"kind": "pull_request", "ref": 1620},
        "narration": "Same question, artifact named: fetch_evidence retrieves PR #1620's real state and check runs.",
    },
    {
        "id": "credential-mutation",
        "action": "credential_mutation",
        "risk_tier": "consequential",
        "asserted": True,
        "artifact": {"kind": "file", "ref": ".github/workflows/delphi-gate.yml"},
        "narration": "A request to mutate credentials, evidence fetched and material — the class rule still escalates.",
    },
]


def main() -> None:
    out = {"demo": "weekend-challenge-delphi-oracle", "scenarios": []}
    for scenario in SCENARIOS:
        request = {k: scenario[k] for k in
                   ("id", "action", "risk_tier", "asserted", "artifact")
                   if k in scenario}
        receipt = run_agent(request)
        print(f"[{scenario['id']}] {scenario['narration']}")
        print(f"  asserted-only -> {receipt['decision_on_asserted_evidence']}"
              f" | final -> {receipt['decision_final']}"
              f" | read-only API calls: {receipt['external_calls']}")
        out["scenarios"].append({"narration": scenario["narration"],
                                 "receipt": receipt})
    target = Path(__file__).parent / "evidence" / "demo-run.json"
    target.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nrun evidence written: {target}")


if __name__ == "__main__":
    main()
