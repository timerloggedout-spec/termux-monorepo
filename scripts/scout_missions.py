#!/usr/bin/env python3
"""Create evidence-first Scout mission proposals from a discovered roster.

Scouts are parallel research/evaluation roles. They propose work to managers;
they do not self-authorize routing, merging, rewards, or promotion.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCOUTS = {
    "provider-research": "discover providers, models, pricing, quota and authoritative availability",
    "code-recon": "mine repository history, PRs, issues, reviews, templates and commits for reusable implementations",
    "performance": "design reproducible performance and correctness experiments",
    "oversight": "find eligible bug bounty, help-wanted, CTF and skills/challenge evaluation targets",
    "regression": "compare proposed work with known-good baselines and detect rollback or evidence loss",
}

OVERSIGHT_CLASSES = (
    "bug-bounty",
    "help-wanted",
    "ctf",
    "developer-skills",
    "security-skills",
    "performance-test",
)


def missions(roster: dict) -> list[dict]:
    candidates = roster.get("candidates", [])
    eligible = [r for r in candidates if r.get("status") == "candidate"]
    result = []
    for scout, purpose in SCOUTS.items():
        target = "provider/model population" if scout != "oversight" else "external evaluation opportunities"
        result.append({
            "scout_id": scout,
            "purpose": purpose,
            "target": target,
            "candidate_count": len(eligible),
            "proposal_only": True,
            "required_evidence": ["source", "observed_at", "provenance", "outcome"],
        })
    return result


def build(roster: dict) -> dict:
    return {
        "schema": "agent-scout-missions/v1",
        "observed_at": roster.get("observed_at"),
        "roster_schema": roster.get("schema"),
        "scouts": missions(roster),
        "oversight_classes": list(OVERSIGHT_CLASSES),
        "governance": {
            "scouts_propose": True,
            "manager_decides": True,
            "evidence_required_for_promotion": True,
            "resource_state_is_not_quality": True,
            "correctness_over_latency": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    roster = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build(roster), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"scouts={len(SCOUTS)} oversight_classes={len(OVERSIGHT_CLASSES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
