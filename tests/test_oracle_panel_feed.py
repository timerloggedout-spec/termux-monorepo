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
- A second point, also cited. (evidence: `y`)

## Unverified / open

- UNVERIFIED: A thing nobody has checked. (evidence refs unresolved at generation time)
"""

PROV = {"proposal_id": "cand-a", "author": "oracle-method",
        "generated_at": "2026-10-27T00:00:00Z", "generator": "gen/v1",
        "pass_id": "pass-1",
        "evidence_sets": [{"sha256": "ab12cd", "items": 3,
                           "assembled_at": "2026-10-27T00:00:00Z"}]}

PASS_META = {"pass_id": "pass-1", "n": 2,
             "candidates": [{"id": "cand-a"}, {"id": "cand-b"}]}
R1 = {"ranked_outcome": ["cand-a", "cand-b"],
      "ballots_by_class": {"HUMAN_COLLABORATOR": 0, "MODEL_PROVIDER": 0,
                           "LOCAL_BASELINE": 5},
      "per_class": {"LOCAL_BASELINE": {"ballots": 5,
                                       "scores": {"cand-a": 30.0, "cand-b": 20.0}},
                    "HUMAN_COLLABORATOR": {"ballots": 0, "scores": {}}},
      "classes_absent": ["HUMAN_COLLABORATOR", "MODEL_PROVIDER"]}
R2 = {"ranked_outcome": ["cand-a", "cand-b"], "evidence_set_sha256": "ab12",
      "ballots_by_class": {"HUMAN_COLLABORATOR": 0, "MODEL_PROVIDER": 0,
                           "LOCAL_BASELINE": 5},
      "per_class": {"LOCAL_BASELINE": {"ballots": 5,
                                        "scores": {"cand-a": 31.5, "cand-b": 19.5}}}}
EXP = {"pass_id": "pass-1", "recorded_before_implementation": True,
       "expectations": {"LOCAL_BASELINE": {
           "cand-a": {"expected_rank": 1, "expected_score": 28.5, "tolerance": 2.0},
           "cand-b": {"expected_rank": 2, "expected_score": 20.0, "tolerance": 2.0}}}}
IMPL_A = {"candidate_id": "cand-a",
          "suites": [{"name": "s1", "passed": 1, "failed": 0},
                     {"name": "s2", "passed": 1, "failed": 0}]}
CAL = {"candidates": {"LOCAL_BASELINE": {
    "cand-a": {"rank_delta": 0, "score_delta": 1.5, "within_tolerance": True,
               "moved_on_evidence": ["full test pass"]},
    "cand-b": {"rank_delta": 0, "score_delta": -0.5, "within_tolerance": True,
               "moved_on_evidence": ["no discriminating test evidence"]}}}}
CYCLE = {"stages": [{"stage": "implementation", "status": "ran", "detail": "ok"},
                    {"stage": "model_panel", "status": "specified_not_run",
                     "detail": "gated"}]}
IMPL_STAGE = {"cand-a": {"suites": [{"name": "s1", "passed": 1, "failed": 0},
                                    {"name": "s2", "passed": 1, "failed": 0}],
                         "passed": 2, "failed": 0, "pass_rate": 1.0},
              "cand-b": {"suites": [], "passed": 0, "failed": 0,
                         "pass_rate": None}}
R1_PROFILES = {"cand-a": {"evidenced_ratio": 1.0},
               "cand-b": {"evidenced_ratio": 0.5}}
EVIDENCE_DOC = {"items": [
    {"claim": "rfp:file.exists", "provenance": {"source": "github-api"}},
    {"claim": "rfp:file.sha", "provenance": {"source": "github-api"}},
    {"claim": "items.open", "provenance": {"source": "manual-record"}}]}

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
    R1["profiles"] = R1_PROFILES
    for name, obj in (("BALLOT-round1.json", R1), ("BALLOT-round2.json", R2),
                      ("CALIBRATION.json", CAL), ("CYCLE.json", CYCLE),
                      ("EXPECTATIONS.json", EXP), ("IMPLEMENTATION.json", IMPL_STAGE)):
        (pdir / "cycle" / name).write_text(json.dumps(obj))
    (pdir / "evidence.json").write_text(json.dumps(EVIDENCE_DOC))
    (pdir / "implementation").mkdir()
    (pdir / "implementation" / "cand-a.json").write_text(json.dumps(IMPL_A))
    stated = passes / "pass-2"
    stated.mkdir()
    (stated / "pass.json").write_text(json.dumps({
        "pass_id": "pass-2", "status": "stated_not_run",
        "n": {"source": "panel.json", "value": 3}, "candidates": []}))
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
    assert a["description"] == ["A point. (evidence: `x`)",
                                 "A second point, also cited. (evidence: `y`)"]
    basis = a["evidence_basis"]
    assert basis["items"] == 3 and basis["sets"][0]["sha256"] == "ab12cd"
    assert basis["sources"] == {"github-api": 2, "manual-record": 1}
    assert basis["claim_areas"] == {"rfp": 2, "items": 1}
    summary = a["implementation_summary"]
    assert summary["suites"] == ["s1", "s2"]
    assert summary["pass_rate"] == 1.0
    assert summary["evidenced_ratio"] == 1.0
    assert summary["all_suites_passed"] is True
    assert feed["sources"]["registry_updated_at"] == "2026-10-27T00:00:00Z"
    assert a["rounds"]["round_1"]["rank_of_this"] == 1
    assert a["rounds"]["round_1"]["scores_by_class"]["LOCAL_BASELINE"] == 30.0
    assert a["rounds"]["round_2"]["scores_by_class"]["LOCAL_BASELINE"] == 31.5
    assert a["expectations"]["LOCAL_BASELINE"] == {
        "expected_rank": 1, "expected_score": 28.5, "tolerance": 2.0}
    assert a["expectations_recorded_before_implementation"] is True
    assert a["implementation"]["passed"] == 2
    assert a["implementation"]["suites_total"] == 2
    assert a["implementation"]["suites_passed"] == 2
    assert a["rounds"]["round_1"]["ballots_by_class"]["HUMAN_COLLABORATOR"] == 0
    assert a["rounds"]["round_1"]["classes_absent"] == ["HUMAN_COLLABORATOR",
                                                        "MODEL_PROVIDER"]
    assert a["calibration"]["LOCAL_BASELINE"]["score_delta"] == 1.5
    snr = {(s["item"], s["reason"]) for s in a["specified_not_run"]}
    assert ("model_panel", "gated") in snr
    assert ("aws_deployment", "card rule") in snr
    assert a["ledger"]["ballot_comment_id"] == 4242
    assert feed["excluded"][0]["label"] == "ideation drafts imagining readiness"
    by_pass = {p["pass_id"]: p for p in feed["passes"]}
    assert by_pass["pass-1"]["status"] == "recorded"
    assert by_pass["pass-1"]["n"] == 2
    # a stated, not-run pass record enters labeled, never as a run pass
    assert by_pass["pass-2"]["status"] == "stated_not_run"
    assert by_pass["pass-2"]["n"] == 3
    assert by_pass["pass-2"]["ranked_outcome"] is None
    assert by_pass["pass-2"]["candidates"] == []


def test_registry_parser_fails_loudly_without_ids():
    try:
        parse_registry("proposals:\n  - title: no id here\n")
    except ValueError:
        return
    raise AssertionError("an id-less registry entry must stop the feed")


ITEMS_MD = """# ITEMS — cand-a

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| SR-001 | Build the thing | proposed | exit: suites green |
| SR-002 | Prove the property | proposed | exit: receipt complete |
"""

PASS_BRIEF = {"variants": [
    {"suffix": "a", "concept": "Concept A",
     "executive_request": "Do A, thoroughly.",
     "summary_points": [{"text": "Point A.", "evidence_refs": ["x"]}],
     "test_suites": ["s1"]},
    {"suffix": "b", "concept": "Concept B",
     "executive_request": "Do B instead.",
     "summary_points": [{"text": "Point B.", "evidence_refs": ["y"]}],
     "test_suites": ["s9"]}]}

PANEL = {"formula": "effective_score = sum(w_i * score_i) / sum(w_i)",
         "criteria": "DECISION-MATRIX 1-25", "seed_note": "seeds only",
         "generation": {"proposals_per_pass": 2,
                        "cross_vote": {"weights_source": "ledger #1489"},
                        "cycle": {"rounds": 2,
                                  "expectation_tolerance": 2.0}}}


def _extend_root(tmp_path):
    """_root plus the depth/provenance records: ITEMS.md per
    candidate, the pass brief, and round-1 ballots + weights."""
    active, passes = _root(tmp_path)
    for cand in ("cand-a", "cand-b"):
        (active / cand / "ITEMS.md").write_text(ITEMS_MD)
    pdir = passes / "pass-1"
    (pdir / "brief.json").write_text(json.dumps(PASS_BRIEF))
    r1_file = pdir / "cycle" / "BALLOT-round1.json"
    r1 = json.loads(r1_file.read_text())
    r1["ballots"] = [{"voter": "rubric:OPERATOR",
                      "source_class": "LOCAL_BASELINE",
                      "scores": {"cand-a": 30, "cand-b": 20}}]
    r1["weights"] = {"source": "ledger weights file ledger-weights.json",
                     "role_weights": {"OPERATOR": 1.4462}}
    r1_file.write_text(json.dumps(r1))
    return active, passes


def test_depth_producers_and_settings(tmp_path):
    active, passes = _extend_root(tmp_path)
    feed = build_feed(REGISTRY, active, passes, {}, False,
                      "2026-10-27T00:00:00Z", panel=PANEL)
    settings = feed["settings"]
    assert settings["generation"]["proposals_per_pass"] == 2
    assert settings["generation"]["expectation_tolerance"] == 2.0
    assert settings["weights_source"] == "ledger #1489"
    a = feed["proposals"][0]
    assert a["approach"]["executive_request"] == "Do A, thoroughly."
    assert a["approach"]["source"].endswith("passes/pass-1/brief.json")
    assert a["summary_points"] == [{"text": "Point A.",
                                     "evidence_refs": ["x"]}]
    assert a["work_items"][0]["id"] == "SR-001"
    assert a["work_items"][1]["state"] == "proposed"
    assert a["documents"]["items"].endswith("active/cand-a/ITEMS.md")
    assert a["evidence_profile"]["evidenced_ratio"] == 1.0
    r1 = a["rounds"]["round_1"]
    assert r1["ballots"][0]["voter"] == "rubric:OPERATOR"
    assert r1["ballots"][0]["score_of_this"] == 30
    assert a["rounds"]["round_2"]["ballots"] is None  # aggregates only
    basis = r1["ranking_basis"]
    assert basis["scores_tied"] is False
    assert basis["score_spread"] == 10.0
    prod = a["producers"]
    assert prod["generation"]["producer"] == "gen/v1"
    lb = prod["rounds"]["round_1"]["LOCAL_BASELINE"]
    assert lb["kind"] == "deterministic_rubric_comparator"
    assert lb["voters"] == ["rubric:OPERATOR"]
    assert lb["weights"]["role_weights"] == {"OPERATOR": 1.4462}
    assert lb["weights"]["ledger_issue"] == 1489
    mp = prod["rounds"]["round_1"]["MODEL_PROVIDER"]
    assert mp["kind"] == "none_recorded" and mp["ballots"] == 0
    assert "DELPHI_LLM_MAX" in mp["reason"]
    hc = prod["rounds"]["round_1"]["HUMAN_COLLABORATOR"]
    assert hc["kind"] == "none_recorded"
    srcs = prod["expectations_sources"]
    assert srcs[0]["source"] == "LOCAL_BASELINE"
    assert srcs[0]["kind"] == "derived_from_round_1"


def test_tied_scores_state_the_tie_break(tmp_path):
    active, passes = _root(tmp_path)
    pdir = passes / "pass-1"
    for name in ("BALLOT-round1.json", "BALLOT-round2.json"):
        f = pdir / "cycle" / name
        doc = json.loads(f.read_text())
        doc["per_class"]["LOCAL_BASELINE"]["scores"] = {
            "cand-a": 23.269, "cand-b": 23.269}
        f.write_text(json.dumps(doc))
    feed = build_feed(REGISTRY, active, passes, {}, False,
                      "2026-10-27T00:00:00Z")
    a = feed["proposals"][0]
    b1 = a["rounds"]["round_1"]["ranking_basis"]
    assert b1["scores_tied"] is True and b1["score_spread"] == 0
    assert "rank()" in b1["decided_by"] and "candidate id" in b1["decided_by"]
    b2 = a["rounds"]["round_2"]["ranking_basis"]
    assert b2["scores_tied"] is True
    assert "method_cycle" in b2["decided_by"]


SOLO_REGISTRY = """version: 1
updated_at: "2026-10-27T00:00:00Z"
proposals:
  - id: solo
    title: A single generation
    author: oracle-method
    status: in_review
    priority: P1
    path: active/solo/
"""


def test_single_generation_uses_its_own_evidence_set(tmp_path):
    active = tmp_path / "active"
    passes = tmp_path / "passes"
    passes.mkdir()
    d = active / "solo"
    d.mkdir(parents=True)
    (d / "MANIFEST.md").write_text(MANIFEST)
    (d / "PROVENANCE.json").write_text(json.dumps(
        {"proposal_id": "solo", "author": "oracle-method",
         "generated_at": "2026-10-27T00:00:00Z", "generator": "gen/v1",
         "evidence_sets": [{"sha256": "cd34ef", "items": 2,
                            "assembled_at": "2026-10-27T00:00:00Z"}]}))
    (d / "evidence.json").write_text(json.dumps({"items": [
        {"claim": "d3:deadline", "provenance": {"source": "github-api"}},
        {"claim": "d3:shape", "provenance": {"source": "github-api"}}]}))
    (d / "ITEMS.md").write_text(ITEMS_MD)
    (d / "brief.json").write_text(json.dumps(
        {"executive_request": "Build the solo thing.",
         "summary_points": [{"text": "Solo point.",
                             "evidence_refs": ["d3:deadline"]}]}))
    feed = build_feed(SOLO_REGISTRY, active, passes, {}, False,
                      "2026-10-27T00:00:00Z")
    solo = feed["proposals"][0]
    assert solo["kind"] == "single" and solo["rounds"] is None
    # The composition comes from the proposal's OWN committed set —
    # null only when no set is committed anywhere for the proposal.
    assert solo["evidence_basis"]["sources"] == {"github-api": 2}
    assert solo["evidence_basis"]["claim_areas"] == {"d3": 2}
    assert solo["approach"]["executive_request"] == "Build the solo thing."
    assert solo["approach"]["source"].endswith("active/solo/brief.json")
    assert solo["summary_points"] == [{"text": "Solo point.",
                                       "evidence_refs": ["d3:deadline"]}]
    assert solo["work_items"][0]["id"] == "SR-001"
    assert solo["producers"]["generation"]["producer"] == "gen/v1"


def test_per_candidate_scores_are_distinct_fields(tmp_path):
    active, passes = _root(tmp_path)
    pdir = passes / "pass-1"
    for name, scores in (("BALLOT-round1.json", {"cand-a": 21.5, "cand-b": 17.25}),
                         ("BALLOT-round2.json", {"cand-a": 22.0, "cand-b": 19.5})):
        f = pdir / "cycle" / name
        doc = json.loads(f.read_text())
        doc["per_class"]["LOCAL_BASELINE"]["scores"] = scores
        doc["classes_present"] = ["LOCAL_BASELINE"]  # as the real receipts carry
        f.write_text(json.dumps(doc))
    feed = build_feed(REGISTRY, active, passes, {}, False,
                      "2026-10-27T00:00:00Z")
    by_id = {p["id"]: p for p in feed["proposals"]}
    # each candidate's rounds carry ITS OWN score as a distinct field,
    # not only a rank inside a shared table
    assert by_id["cand-a"]["rounds"]["round_1"]["score"] == 21.5
    assert by_id["cand-b"]["rounds"]["round_1"]["score"] == 17.25
    assert by_id["cand-a"]["rounds"]["round_2"]["score"] == 22.0
    assert by_id["cand-b"]["rounds"]["round_2"]["score"] == 19.5
    assert by_id["cand-a"]["rounds"]["round_1"]["scores_by_class"][
        "LOCAL_BASELINE"] == 21.5
