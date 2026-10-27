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

IMPL = {
    "rehearsal-strong": {"suites": [{"name": "concept", "passed": 4, "failed": 0}]},
    "rehearsal-weak": {"suites": [{"name": "concept", "passed": 1, "failed": 3}]},
    "rehearsal-empty": {"suites": [{"name": "concept", "passed": 0, "failed": 2}]},
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
    assert all(v == "ran" for v in st.values()), st
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
