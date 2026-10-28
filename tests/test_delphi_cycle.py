"""Offline tests for the N5 Delphi-cycle workflow build.

Pins the brief (docs/rfps/temporal-durable-execution/
N5-BUILD-BRIEF.md): ballot validation identical to cycle v2 with
rejections recorded (never silent), round-2's equalized-evidence
gate, the phantom-rule transform's parity with method_cycle, the
staged activities' parity with run_cycle on the rehearsal fixture,
and ledger emission's exactly-once shape in record_only mode. The
live proof is the brief §5 acceptance (client.py prove), not a unit
test.
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))
sys.path.insert(0, str(ROOT / "scripts" / "temporal"))

from method_cycle import run_cycle  # noqa: E402
from test_delphi_cross_vote import EVIDENCE, PANEL, PASS_BRIEF  # noqa: E402
from generate_proposal import generate_pass  # noqa: E402


def _load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, ROOT.joinpath(*parts))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wf_mod = _load("delphi_cycle_workflow",
               "scripts", "temporal", "delphi_cycle", "workflow.py")
act_mod = _load("delphi_cycle_activities",
                "scripts", "temporal", "delphi_cycle", "activities.py")

BallotSignal = wf_mod.BallotSignal
validate_ballot = wf_mod.validate_ballot
CANDS = ["rehearsal-strong", "rehearsal-weak", "rehearsal-empty"]
SCORES = {"rehearsal-strong": 20, "rehearsal-weak": 10, "rehearsal-empty": 5}
CONFIG = {"rounds": 2, "expectation_tolerance": 2.0}
GENERATED_AT = "2026-10-27T00:00:00Z"


def _ballot(**kw):
    base = {"voter": "registrar:owner", "source_class": "HUMAN_COLLABORATOR",
            "round": 1, "scores": dict(SCORES), "rationale": "reasons",
            "evidence_refs": ["fixture"]}
    base.update(kw)
    return BallotSignal(**base)


def _validate(ballot, **kw):
    args = {"round_no": ballot.round, "candidate_ids": CANDS,
            "bundle_sha256": None, "seen_keys": set()}
    args.update(kw)
    return validate_ballot(ballot, **args)


def test_valid_round1_ballot_admitted():
    assert _validate(_ballot()) is None


def test_reasonless_ballot_rejected():
    assert "rationale" in _validate(_ballot(rationale=None))


def test_refless_ballot_rejected():
    assert "evidence" in _validate(_ballot(evidence_refs=[]))


def test_driver_synthesis_is_not_a_ballot():
    reason = _validate(_ballot(source_class="DRIVER_SYNTHESIS"))
    assert "DRIVER_SYNTHESIS" in reason


def test_duplicate_ballot_rejected():
    seen = {(1, "HUMAN_COLLABORATOR", "registrar:owner", None)}
    assert "duplicate" in _validate(_ballot(), seen_keys=seen)
    # …but the same voter in round 2 is a fresh ballot, not a dupe
    # (live prove attempt 3, 2026-10-28: cross-round collision
    # rejected every round-2 ballot from the round-1 registrar).
    r2 = _ballot(round=2, evidence_bundle_sha256="abc")
    assert _validate(r2, bundle_sha256="abc", seen_keys=seen) is None


def test_model_ballot_needs_run_record():
    reason = _validate(_ballot(source_class="MODEL_PROVIDER"))
    assert "run record" in reason
    ok = _ballot(source_class="MODEL_PROVIDER",
                 run={"provider": "p", "model": "m", "run_id": "r1",
                      "response_hash": "h", "entitlement": "no-cost"})
    assert _validate(ok) is None


def test_round2_requires_the_bundle_hash():
    b = _ballot(round=2)
    assert "sha256" in _validate(b, bundle_sha256="abc")
    wrong = _ballot(round=2, evidence_bundle_sha256="zzz")
    assert "different evidence bundle" in _validate(wrong,
                                                    bundle_sha256="abc")
    good = _ballot(round=2, evidence_bundle_sha256="abc")
    assert _validate(good, bundle_sha256="abc") is None


def test_ballot_for_wrong_round_rejected():
    reason = validate_ballot(_ballot(round=2), round_no=1,
                             candidate_ids=CANDS, bundle_sha256=None,
                             seen_keys=set())
    assert "round 1 is open" in reason


# ------------------------------------------------------------ parity

def _receipt():
    return {"command": "pytest tests/test_fixture.py", "exit_code": 0,
            "output_sha256": "0" * 64, "code_paths": ["scripts/fixture.py"]}


IMPL = {
    "rehearsal-strong": {"suites": [{"name": "concept", "passed": 4,
                                     "failed": 0, "receipt": _receipt()}]},
    "rehearsal-weak": {"suites": [{"name": "concept", "passed": 1,
                                   "failed": 3, "receipt": _receipt()}]},
    "rehearsal-empty": {"suites": [{"name": "concept", "passed": 0,
                                    "failed": 2, "receipt": _receipt()}]},
}


def _meta():
    _, meta = generate_pass(PASS_BRIEF, EVIDENCE, generated_at=GENERATED_AT)
    return meta


def test_phantom_transform_matches_run_cycle():
    phantom = json.loads(json.dumps(IMPL))
    del phantom["rehearsal-strong"]["suites"][0]["receipt"]
    impl, unreceipted = act_mod.apply_phantom_rule(phantom, CANDS, CONFIG)
    cycle = run_cycle(_meta(), PANEL["roles"], "test", CONFIG,
                      impl_results=json.loads(json.dumps(phantom)),
                      generated_at=GENERATED_AT)
    assert impl == cycle["artifacts"]["implementation"]
    assert unreceipted == ["rehearsal-strong:concept"]


def test_staged_activities_match_run_cycle_artifacts(tmp_path):
    meta = _meta()
    r1_ballots = [{"voter": "registrar:owner",
                   "source_class": "HUMAN_COLLABORATOR",
                   "scores": dict(SCORES), "rationale": "reasons",
                   "evidence_refs": ["fixture"]}]
    round1 = act_mod.cross_vote_round1_activity({
        "pass_id": "rehearsal", "pass_meta": meta,
        "panel_roles": PANEL["roles"], "weights_source": "test",
        "ballots": r1_ballots, "generated_at": GENERATED_AT})
    exp_synth = act_mod.expectations_synthesis_activity({
        "pass_meta": meta, "round1": round1, "round1_ballots": r1_ballots,
        "panel_roles": PANEL["roles"], "config": CONFIG,
        "recorded_expectations": None})
    equalized = act_mod.equalize_activity({
        "pass_id": "rehearsal", "pass_meta": meta,
        "impl_results": json.loads(json.dumps(IMPL)), "config": CONFIG})
    cycle = run_cycle(meta, PANEL["roles"], "test", CONFIG,
                      round1_ballots=r1_ballots,
                      impl_results=json.loads(json.dumps(IMPL)),
                      generated_at=GENERATED_AT)
    assert round1 == {**cycle["artifacts"]["round1"],
                      "pass_id": "rehearsal"}
    assert exp_synth["expectations"] == cycle["artifacts"]["expectations"]
    assert exp_synth["synthesis"] == cycle["artifacts"]["synthesis"]
    assert equalized["impl"] == cycle["artifacts"]["implementation"]
    assert equalized["evidence_sha256"] == \
        cycle["artifacts"]["round2_evidence"]["sha256"]


def test_finalize_and_record_only_emission(tmp_path):
    meta = _meta()
    round1 = act_mod.cross_vote_round1_activity({
        "pass_id": "rehearsal", "pass_meta": meta,
        "panel_roles": PANEL["roles"], "weights_source": "test",
        "ballots": [], "generated_at": GENERATED_AT})
    exp_synth = act_mod.expectations_synthesis_activity({
        "pass_meta": meta, "round1": round1, "round1_ballots": [],
        "panel_roles": PANEL["roles"], "config": CONFIG,
        "recorded_expectations": None})
    equalized = act_mod.equalize_activity({
        "pass_id": "rehearsal", "pass_meta": meta,
        "impl_results": json.loads(json.dumps(IMPL)), "config": CONFIG})
    slim = act_mod.finalize_cycle_activity({
        "pass_id": "rehearsal", "workdir": str(tmp_path),
        "pass_meta": meta, "panel_roles": PANEL["roles"],
        "weights_source": "test", "config": CONFIG,
        "round1_ballots": [], "round2_ballots": [],
        "impl_results": json.loads(json.dumps(IMPL)),
        "recorded_expectations": None, "generated_at": GENERATED_AT,
        "expectations": exp_synth["expectations"],
        "impl_transformed": equalized["impl"],
        "evidence_sha256": equalized["evidence_sha256"]})
    assert slim["ranked_outcome"][0] == "rehearsal-strong"
    assert (tmp_path / "rehearsal" / "cycle" / "CYCLE.json").exists()
    emission = act_mod.emit_records_activity({
        "pass_id": "rehearsal", "workdir": str(tmp_path),
        "workflow_id": "delphi-cycle/rehearsal",
        "ledger_mode": "record_only"})
    states = {r["stage"]: r["state"] for r in emission["receipts"]}
    assert states["ballot_round1"] == "recorded_only"
    assert states["calibration"] == "recorded_only"
    body = (tmp_path / "rehearsal" / "cycle" /
            "EMIT-ballot_round1.md").read_text()
    assert "<!-- n5-emit:delphi-cycle/rehearsal:ballot_round1 -->" in body
    assert "<!-- delphi-generation-ballot v1 -->" in body


def test_ballot_signal_survives_payload_conversion():
    # Regression (live prove attempt 1, 2026-10-28): rationale typed
    # as `object` failed temporalio's payload conversion and the
    # signal was lost. Every signal dataclass must round-trip.
    from temporalio.converter import DefaultPayloadConverter
    conv = DefaultPayloadConverter.default
    for obj in (_ballot(), _ballot(round=2, evidence_bundle_sha256="x"),
                wf_mod.FacilitatorSignal(action="open_round_2", by="f")):
        payloads = conv.to_payloads([obj])
        back = conv.from_payloads(payloads, [type(obj)])
        assert back[0] == obj


def test_worker_is_cycle_scoped_not_a_daemon():
    # Amendment 2026-10-28 (VM = sandbox only): the worker's bounded
    # mode exists and no systemd unit ships for it.
    src = (ROOT / "scripts" / "temporal" / "delphi_cycle" /
           "worker.py").read_text()
    assert "--exit-on-complete" in src
    assert not (ROOT / "scripts" / "temporal" / "selfhost" /
                "temporal-delphi-worker.service").exists()


def test_workflow_module_is_deterministic_shape():
    # The workflow module must not reach for I/O, clocks, or randomness:
    # a static guard over its source (the sandbox enforces it live).
    src = (ROOT / "scripts" / "temporal" / "delphi_cycle" /
           "workflow.py").read_text()
    for banned in ("import os", "import subprocess", "datetime.now",
                   "time.time", "random.", "open("):
        assert banned not in src, banned
    assert "wait_condition" in src  # signal gates, not sleeps
