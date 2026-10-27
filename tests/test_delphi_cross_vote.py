"""Offline tests: generation passes (n candidates) + the cross-vote.

Pins the owner parameter (2026-10-27): a pass emits n proposals and
they are cross-voted — comparative ballots, source classes separate
per the DEBATE protocol, existing panel weighting for aggregation,
zero-ballot classes reported as zero, never filled in.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))

from cross_vote import cross_vote, load_ledger_weights, role_weight  # noqa: E402
from generate_proposal import generate_pass  # noqa: E402

EVIDENCE = [{
    "schema": "delphi-evidence-set/v1", "assembled_at": "2026-10-27T00:00:00Z",
    "items": [
        {"claim": "a.claim", "value": 1,
         "provenance": {"source": "github-api", "path": "/x", "observed_at": "2026-10-27T00:00:00Z"},
         "fresh_until": "2026-10-27T00:15:00Z", "sha256": "a" * 64},
        {"claim": "b.claim", "value": 2,
         "provenance": {"source": "github-api", "path": "/y", "observed_at": "2026-10-27T00:00:00Z"},
         "fresh_until": "2026-10-27T00:15:00Z", "sha256": "b" * 64},
    ],
}]

PASS_BRIEF = {
    "id": "rehearsal", "title": "Rehearsal pass", "kind": "competition",
    "surface": "Test", "priority": "P2", "item_prefix": "RH",
    "variants": [
        {"suffix": "strong", "concept": "fully evidenced",
         "summary_points": [{"text": "p1", "evidence_refs": ["a.claim"]},
                            {"text": "p2", "evidence_refs": ["b.claim"]}],
         "items": [{"item": "build", "state": "proposed", "evidence": "x"}]},
        {"suffix": "weak", "concept": "half evidenced",
         "summary_points": [{"text": "p1", "evidence_refs": ["a.claim"]},
                            {"text": "p2", "evidence_refs": ["missing.claim"]}],
         "items": [{"item": "build", "state": "proposed", "evidence": "x"},
                   {"item": "needs an account and a card", "state": "proposed",
                    "evidence": "y"}]},
        {"suffix": "empty", "concept": "no evidenced points",
         "summary_points": [{"text": "p1", "evidence_refs": ["nope"]}],
         "items": [{"item": "build", "state": "proposed", "evidence": "x"}]},
    ],
}

PANEL = {"roles": {
    "OPERATOR": {"base": 1.2, "gate_pass_rate": 0.68, "elo": 1532},
    "builder": {"base": 1.0, "gate_pass_rate": 0.68, "elo": 1532},
    "reviewer": {"base": 1.0, "gate_pass_rate": 0.68, "elo": 1532},
    "Scout": {"base": 0.8, "gate_pass_rate": 0.68, "elo": 1532},
    "cost_auditor": {"base": 1.2, "gate_pass_rate": 0.68, "elo": 1532},
}}


def _run(extra=None):
    docs_by_dir, meta = generate_pass(PASS_BRIEF, EVIDENCE,
                                      generated_at="2026-10-27T00:00:00Z")
    candidates = [{"id": c["id"], "profile": c["profile"]}
                  for c in meta["candidates"]]
    return docs_by_dir, meta, cross_vote(candidates, PANEL["roles"],
                                         "test weights", extra,
                                         generated_at="2026-10-27T00:00:00Z")


def test_pass_emits_n_candidates_with_profiles():
    docs_by_dir, meta, _ = _run()
    assert meta["n"] == 3
    assert sorted(docs_by_dir) == ["rehearsal-empty", "rehearsal-strong",
                                   "rehearsal-weak"]
    profiles = {c["id"]: c["profile"] for c in meta["candidates"]}
    assert profiles["rehearsal-strong"]["evidenced_ratio"] == 1.0
    assert profiles["rehearsal-weak"]["evidenced_ratio"] == 0.5
    assert profiles["rehearsal-empty"]["evidenced_ratio"] == 0.0


def test_cross_vote_ranks_by_evidence_and_reports_absent_classes():
    _, _, receipt = _run()
    assert receipt["ranked_outcome"][0] == "rehearsal-strong"
    assert receipt["ranked_outcome"][-1] == "rehearsal-empty"
    assert receipt["ballots_by_class"] == {"HUMAN_COLLABORATOR": 0,
                                           "MODEL_PROVIDER": 0,
                                           "LOCAL_BASELINE": 5}
    assert receipt["classes_absent"] == ["HUMAN_COLLABORATOR", "MODEL_PROVIDER"]
    assert receipt["combined_ranking"] is None  # only one class cast ballots


def test_human_ballots_tallied_separately_and_combined_ranking_appears():
    human = [{"voter": "registrar:owner", "source_class": "HUMAN_COLLABORATOR",
              "scores": {"rehearsal-strong": 10, "rehearsal-weak": 24,
                         "rehearsal-empty": 5}}]
    _, _, receipt = _run(extra=human)
    assert receipt["ballots_by_class"]["HUMAN_COLLABORATOR"] == 1
    assert receipt["per_class"]["HUMAN_COLLABORATOR"]["ranking"][0] == "rehearsal-weak"
    assert receipt["per_class"]["LOCAL_BASELINE"]["ranking"][0] == "rehearsal-strong"
    assert receipt["combined_ranking"] is not None
    assert receipt["combined_ranking"][0] in ("rehearsal-strong", "rehearsal-weak")


def test_driver_synthesis_is_not_a_ballot():
    bad = [{"voter": "x", "source_class": "DRIVER_SYNTHESIS",
            "scores": {"rehearsal-strong": 25}}]
    try:
        _run(extra=bad)
    except ValueError:
        return
    raise AssertionError("DRIVER_SYNTHESIS ballots must be refused")


def test_role_weight_formula_and_ledger_loader():
    assert abs(role_weight({"base": 1.2, "gate_pass_rate": 0.68, "elo": 1532})
               - 1.2 * 1.18 * (1532 / 1500)) < 1e-9
    comments = [{"body": "noise"},
                {"body": "<!-- delphi-weights v1 -->\n```json\n"
                         "{\"roles\": {\"OPERATOR\": {\"base\": 1.2, "
                         "\"gate_pass_rate\": 0.68, \"elo\": 1532}}}\n```"}]
    weights = load_ledger_weights(comments)
    assert weights["roles"]["OPERATOR"]["elo"] == 1532
