"""Offline tests for the Oracle Panel feed collector.

The feed's contract is honesty: only oracle-method registry entries,
only what the records hold, classes absent as recorded, UNVERIFIED
and specified_not_run carried as first-class values, rehearsals
excluded by construction (they are never in the registry).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))

from oracle_panel_feed import build_feed, ledger_payloads, parse_registry  # noqa: E402

REGISTRY = """version: 1
updated_at: "2026-10-27T00:00:00Z"
updated_by: oracle-method
proposals:
  - id: human-one
    title: A human proposal
    author: ChatGPT
    status: posted
    path: active/human-one/
  - id: cand-a
    title: Candidate A
    author: oracle-method
    status: in_review
    priority: P1
    path: active/cand-a/
  - id: cand-b
    title: Candidate B
    author: oracle-method
    status: in_review
    priority: P1
    path: active/cand-b/
"""

MANIFEST = """# MANIFEST — cand-a

## Summary

- A point. (evidence: `x`)

## Unverified / open

- UNVERIFIED: A thing nobody has checked. (evidence refs unresolved at generation time)
"""

PROV = {"proposal_id": "cand-a", "author": "oracle-method",
        "generated_at": "2026-10-27T00:00:00Z", "generator": "gen/v1",
        "pass_id": "pass-1", "evidence_sets": [{"items": 7}]}

PASS_META = {"pass_id": "pass-1", "n": 2,
             "candidates": [{"id": "cand-a"}, {"id": "cand-b"}]}
R1 = {"ranked_outcome": ["cand-a", "cand-b"],
      "ballots_by_class": {"HUMAN_COLLABORATOR": 0, "MODEL_PROVIDER": 0,
                           "LOCAL_BASELINE": 5},
      "classes_absent": ["HUMAN_COLLABORATOR", "MODEL_PROVIDER"]}
R2 = {"ranked_outcome": ["cand-a", "cand-b"], "evidence_set_sha256": "ab12",
      "ballots_by_class": {"HUMAN_COLLABORATOR": 0, "MODEL_PROVIDER": 0,
                           "LOCAL_BASELINE": 5}}
CAL = {"candidates": {"LOCAL_BASELINE": {
    "cand-a": {"rank_delta": 0, "score_delta": 1.5, "within_tolerance": True,
               "moved_on_evidence": ["full test pass"]},
    "cand-b": {"rank_delta": 0, "score_delta": -0.5, "within_tolerance": True,
               "moved_on_evidence": ["no discriminating test evidence"]}}}}
CYCLE = {"stages": [{"stage": "implementation", "status": "ran", "detail": "ok"},
                    {"stage": "model_panel", "status": "specified_not_run",
                     "detail": "gated"}]}

LEDGER_COMMENTS = [{
    "id": 4242,
    "body": "<!-- delphi-generation-ballot v1 -->\n```json\n"
            + json.dumps({"pass_id": "pass-1",
                          "specified_not_run": {"aws_deployment": "card rule"}})
            + "\n```"}]


def _root(tmp_path):
    active = tmp_path / "active"
    passes = tmp_path / "passes"
    for cand in ("cand-a", "cand-b"):
        d = active / cand
        d.mkdir(parents=True)
        (d / "MANIFEST.md").write_text(MANIFEST)
        (d / "PROVENANCE.json").write_text(json.dumps(
            {**PROV, "proposal_id": cand}))
    pdir = passes / "pass-1"
    (pdir / "cycle").mkdir(parents=True)
    (pdir / "pass.json").write_text(json.dumps(PASS_META))
    for name, obj in (("BALLOT-round1.json", R1), ("BALLOT-round2.json", R2),
                      ("CALIBRATION.json", CAL), ("CYCLE.json", CYCLE)):
        (pdir / "cycle" / name).write_text(json.dumps(obj))
    return active, passes


def test_feed_carries_only_what_the_record_holds(tmp_path):
    active, passes = _root(tmp_path)
    ledger = ledger_payloads(LEDGER_COMMENTS)
    feed = build_feed(REGISTRY, active, passes, ledger, True,
                      "2026-10-27T00:00:00Z")
    assert feed["sources"]["registry_proposals_total"] == 3
    ids = [p["id"] for p in feed["proposals"]]
    assert ids == ["cand-a", "cand-b"]  # non-oracle entry excluded
    a = feed["proposals"][0]
    assert a["unverified_points"] == ["A thing nobody has checked. "
                                      "(evidence refs unresolved at generation time)"]
    assert a["rounds"]["round_1"]["rank_of_this"] == 1
    assert a["rounds"]["round_1"]["ballots_by_class"]["HUMAN_COLLABORATOR"] == 0
    assert a["rounds"]["round_1"]["classes_absent"] == ["HUMAN_COLLABORATOR",
                                                        "MODEL_PROVIDER"]
    assert a["calibration"]["LOCAL_BASELINE"]["score_delta"] == 1.5
    snr = {(s["item"], s["reason"]) for s in a["specified_not_run"]}
    assert ("model_panel", "gated") in snr
    assert ("aws_deployment", "card rule") in snr
    assert a["ledger"]["ballot_comment_id"] == 4242
    assert feed["excluded"][0]["label"] == "ideation drafts imagining readiness"


def test_registry_parser_fails_loudly_without_ids():
    try:
        parse_registry("proposals:\n  - title: no id here\n")
    except ValueError:
        return
    raise AssertionError("an id-less registry entry must stop the feed")
