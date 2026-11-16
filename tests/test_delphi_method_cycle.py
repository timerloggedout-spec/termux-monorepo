"""Offline tests for the Oracle Method full cycle.

Pins the owner spec (2026-10-27): expectations recorded before
implementation; implementation results become the single equalized
round-2 evidence base (hash-gated); round 2 re-votes on it; calibration
compares round 2 against the recorded expectations; a stage that
cannot run is recorded specified_not_run, never fabricated.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))

from method_cycle import run_cycle  # noqa: E402
from test_delphi_cross_vote import EVIDENCE, PANEL, PASS_BRIEF  # noqa: E402
from generate_proposal import generate_pass  # noqa: E402

CONFIG = {"rounds": 2, "expectation_tolerance": 2.0}

def _receipt():
    return {"command": "pytest tests/test_fixture.py", "exit_code": 0,
            "output_sha256": "0" * 64, "code_paths": ["scripts/fixture.py"]}


IMPL = {
    "rehearsal-strong": {"suites": [{"name": "concept", "passed": 4, "failed": 0,
                                     "receipt": _receipt()}]},
    "rehearsal-weak": {"suites": [{"name": "concept", "passed": 1, "failed": 3,
                                   "receipt": _receipt()}]},
    "rehearsal-empty": {"suites": [{"name": "concept", "passed": 0, "failed": 2,
                                    "receipt": _receipt()}]},
}


def _meta():
    _, meta = generate_pass(PASS_BRIEF, EVIDENCE,
                            generated_at="2026-10-27T00:00:00Z")
    return meta


def _statuses(cycle):
    return {s["stage"]: s["status"] for s in cycle["stages"]}


def test_full_cycle_runs_all_stages_and_calibrates():
    cycle = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                      impl_results=IMPL, generated_at="2026-10-27T00:00:00Z")
    st = _statuses(cycle)
    assert st["facilitator_feedback"] == "ran"
    assert st["debate_revision"] == "specified_not_run"  # callable, not called
    ran = [k for k, v in st.items() if k != "debate_revision"]
    assert all(st[k] == "ran" for k in ran), st
    syn = cycle["artifacts"]["synthesis"]
    assert syn["schema"] == "delphi-facilitator-synthesis/v1"
    strong = syn["candidates"]["rehearsal-strong"]
    assert strong["arguments"], "the synthesis carries the voters' own reasons"
    assert strong["scores_by_class"]["LOCAL_BASELINE"]["n"] == 5
    cal = cycle["artifacts"]["calibration"]["candidates"]["LOCAL_BASELINE"]
    # the failing implementations drop against their round-1 expectations
    assert cal["rehearsal-weak"]["score_delta"] < 0
    assert cal["rehearsal-weak"]["moved_on_evidence"]
    assert cal["rehearsal-strong"]["expected_rank"] == 1
    assert cycle["ledger_feed"]["type"] == "delphi-generation-calibration"


def test_expectations_are_recorded_before_and_independent_of_implementation():
    bare = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                     generated_at="2026-10-27T00:00:00Z")
    full = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                     impl_results=IMPL, generated_at="2026-10-27T00:00:00Z")
    assert bare["artifacts"]["expectations"] == full["artifacts"]["expectations"]
    assert bare["artifacts"]["expectations"]["recorded_before"] == "implementation"


def test_missing_implementation_records_specified_not_run():
    cycle = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                      generated_at="2026-10-27T00:00:00Z")
    st = _statuses(cycle)
    assert st["cross_vote_round_1"] == "ran"
    assert st["expectations_recorded"] == "ran"
    for stage in ("implementation", "evidence_equalization",
                  "cross_vote_round_2", "calibration"):
        assert st[stage] == "specified_not_run", stage
    assert cycle["ledger_feed"] is None


def test_round2_ballot_must_carry_the_equalized_evidence_hash():
    good = [{"voter": "registrar:owner", "source_class": "HUMAN_COLLABORATOR",
             "evidence_set_sha256": "will-not-match",
             "rationale": "judged on the bundle I was shown",
             "evidence_refs": ["round-2 evidence bundle"],
             "scores": {"rehearsal-strong": 20, "rehearsal-weak": 10,
                        "rehearsal-empty": 5}}]
    try:
        run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                  impl_results=IMPL, round2_ballots=good,
                  generated_at="2026-10-27T00:00:00Z")
    except ValueError as exc:
        assert "equalized evidence hash" in str(exc)
        return
    raise AssertionError("a round-2 ballot on other evidence must be rejected")


def test_partial_implementation_results_fail_loudly():
    partial = {"rehearsal-strong": IMPL["rehearsal-strong"]}
    try:
        run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                  impl_results=partial, generated_at="2026-10-27T00:00:00Z")
    except ValueError as exc:
        assert "missing" in str(exc)
        return
    raise AssertionError("missing per-proposal results must fail, not default")


def test_brief_priors_coexist_with_derived_and_calibrate():
    brief_priors = {"author": "challenge-entries-lane",
                    "expectations": {
                        "rehearsal-strong": {"expected_rank": 1, "expected_score": 19},
                        "rehearsal-weak": {"expected_rank": 2, "expected_score": 17},
                        "rehearsal-empty": {"expected_rank": 3, "expected_score": 14}}}
    cycle = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                      impl_results=IMPL, recorded_expectations=brief_priors,
                      generated_at="2026-10-27T00:00:00Z")
    exp = cycle["artifacts"]["expectations"]["expectations"]
    assert "LOCAL_BASELINE" in exp            # derived priors still recorded
    assert "BRIEF:challenge-entries-lane" in exp
    cal = cycle["artifacts"]["calibration"]["candidates"]
    assert "BRIEF:challenge-entries-lane" in cal
    assert "LOCAL_BASELINE" in cal
    brief_cal = cal["BRIEF:challenge-entries-lane"]
    assert brief_cal["rehearsal-weak"]["score_delta"] < 0  # priors vs round-2 reality


def test_eligibility_gate_refuses_early_implementation():
    gated = dict(PASS_BRIEF, eligibility_gate={
        "rule": "only in-period projects eligible",
        "window_open": "2026-10-30T13:00:00-07:00"})
    docs_by_dir, meta = generate_pass(gated, EVIDENCE,
                                      generated_at="2026-10-27T00:00:00Z")
    assert meta["eligibility_gate"]["window_open"] == "2026-10-30T13:00:00-07:00"
    import json as _json
    prov = _json.loads(docs_by_dir["rehearsal-strong"]["PROVENANCE.json"])
    assert prov["eligibility_gate"]["window_open"].startswith("2026-10-30")

    early = run_cycle(meta, PANEL["roles"], "test", CONFIG,
                      impl_results=IMPL, generated_at="2026-10-29T00:00:00Z")
    st = _statuses(early)
    detail = next(s["detail"] for s in early["stages"]
                  if s["stage"] == "implementation")
    assert st["implementation"] == "specified_not_run"
    assert "eligibility gate" in detail
    assert st["cross_vote_round_1"] == "ran"  # generation + vote are not gated

    after = run_cycle(meta, PANEL["roles"], "test", CONFIG,
                      impl_results=IMPL, generated_at="2026-10-31T00:00:00Z")
    assert _statuses(after)["implementation"] == "ran"


def test_debate_revision_round_is_callable_after_cycle_1():
    revised = [{"voter": "registrar:owner",
                "source_class": "HUMAN_COLLABORATOR",
                "rationale": "the synthesis showed weak's argument rests "
                             "on an unverified point",
                "evidence_refs": ["SYNTHESIS.json"],
                "revision_reason": "revised weak down; retained the rest",
                "scores": {"rehearsal-strong": 20, "rehearsal-weak": 8,
                           "rehearsal-empty": 5}}]
    cycle = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                      impl_results=IMPL, feedback_ballots=revised,
                      generated_at="2026-10-27T00:00:00Z")
    st = _statuses(cycle)
    assert st["debate_revision"] == "ran"
    fb = cycle["artifacts"]["feedback"]
    assert fb["per_class"]["HUMAN_COLLABORATOR"]["ranking"][0] == \
        "rehearsal-strong"
    no_reason = [dict(revised[0])]
    del no_reason[0]["revision_reason"]
    try:
        run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                  impl_results=IMPL, feedback_ballots=no_reason,
                  generated_at="2026-10-27T00:00:00Z")
    except ValueError as exc:
        assert "revision_reason" in str(exc)
    else:
        raise AssertionError("a revision without its reason must be refused")


def test_unreceipted_suites_earn_no_passes():
    phantom = {
        "rehearsal-strong": {"suites": [{"name": "concept", "passed": 4,
                                         "failed": 0}]},  # no receipt
        "rehearsal-weak": IMPL["rehearsal-weak"],
        "rehearsal-empty": IMPL["rehearsal-empty"],
    }
    cycle = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                      impl_results=phantom,
                      generated_at="2026-10-27T00:00:00Z")
    impl = cycle["artifacts"]["implementation"]["rehearsal-strong"]
    assert impl["passed"] == 0 and impl["pass_rate"] == 0.0
    assert impl["suites"][0]["unverified"] is True
    stage = next(s for s in cycle["stages"] if s["stage"] == "implementation")
    assert "UNRECEIPTED" in stage["detail"]
