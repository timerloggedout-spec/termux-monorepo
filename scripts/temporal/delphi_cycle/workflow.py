"""DelphiCycleWorkflow — the Oracle Method cycle as a durable process.

N5 (RFP docs/rfps/temporal-durable-execution/RFP.md §7, build brief
N5-BUILD-BRIEF.md): the cycle v2 semantics of scripts/delphi/
{generate_proposal,cross_vote,method_cycle}.py, moved onto the fleet
Temporal self-host WITHOUT changing them. Stage work lives in
activities (activities.py) which wrap that machinery; this workflow
only orchestrates: signal intake + validation, the facilitator gate,
stage sequencing, and the CycleStatus projection.

Determinism: no I/O, no wall-clock reads, no randomness in here.
`generated_at` arrives in the input (stamped by the client at start)
so a replay — and the dual-run parity check against method_cycle.py —
sees one fixed clock.

Ballots are signals. Validation is cycle v2's (cross_vote.
validate_ballots intake rules, restated as a pure function so the
workflow sandbox can run it): voter + rationale + evidence_refs
required; source classes separate, never merged; DRIVER_SYNTHESIS is
not a ballot; MODEL_PROVIDER ballots need their run record; dedupe on
(source_class, voter, run_id). Round-2 ballots are REJECTED — and the
rejection recorded with its reason — unless they carry the equalized
evidence bundle sha256 issued by the equalize stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from temporalio import workflow

CLASSES = ("HUMAN_COLLABORATOR", "MODEL_PROVIDER", "LOCAL_BASELINE")
TASK_QUEUE = "delphi-cycle"

# Activity names (string form: the workflow never imports activity
# code, keeping the sandbox free of I/O modules).
ACT_GENERATE = "generate_pass_activity"
ACT_ROUND1 = "cross_vote_round1_activity"
ACT_EXPECT_SYNTH = "expectations_synthesis_activity"
ACT_IMPL = "run_implementation_suites_activity"
ACT_EQUALIZE = "equalize_activity"
ACT_FINALIZE = "finalize_cycle_activity"
ACT_EMIT = "emit_records_activity"


@dataclass
class BallotSignal:
    """One comparative ballot, cast by signal (brief §2)."""
    voter: str = ""
    source_class: str = ""
    round: int = 0
    scores: dict = field(default_factory=dict)
    rationale: Any = None             # str or {candidate: str}
    evidence_refs: list = field(default_factory=list)
    evidence_bundle_sha256: str | None = None
    run: dict | None = None           # MODEL_PROVIDER run record
    revision_reason: str | None = None


@dataclass
class FacilitatorSignal:
    """Facilitator control: close_round_1 | open_round_2 | close_round_2."""
    action: str = ""
    by: str = ""
    note: str = ""


@dataclass
class CycleInput:
    pass_brief: dict = field(default_factory=dict)     # generate_proposal pass brief (with variants)
    evidence_sets: list = field(default_factory=list)  # fetch_evidence sets
    panel_roles: dict = field(default_factory=dict)    # panel.json roles (or ledger weights roles)
    weights_source: str = "panel.json cold-start defaults"
    config: dict = field(default_factory=dict)         # panel.json generation.cycle
    suite_specs: dict = field(default_factory=dict)    # candidate -> [{name, argv, code_paths}]
    recorded_expectations: dict | None = None          # brief-supplied priors
    generated_at: str = ""                             # stamped once by the client
    workdir: str = ""                                  # worker-host durable dir for artifacts
    ledger_mode: str = "github"                        # github | record_only (tests)


def validate_ballot(ballot: BallotSignal, *, round_no: int,
                    candidate_ids: list[str],
                    bundle_sha256: str | None,
                    seen_keys: set) -> str | None:
    """Cycle-v2 ballot validation. Returns None when the ballot is
    admissible, else the rejection reason (recorded, never silent).

    Mirrors cross_vote.validate_ballots + the round-2 evidence gate
    from method_cycle.run_cycle stage 5 — the workflow applies them at
    signal time so a bad ballot is refused at the door instead of
    aborting the cycle at aggregation time (brief §2: rejected AND
    recorded).
    """
    if ballot.round != round_no:
        return f"ballot is for round {ballot.round}; round {round_no} is open"
    if not ballot.voter:
        return "ballot without a voter identity"
    if ballot.source_class not in CLASSES:
        return (f"unaccepted source_class: {ballot.source_class!r} "
                "(DRIVER_SYNTHESIS is not a ballot)")
    if not ballot.rationale:
        return ("carries no rationale — a Delphi response is a judgment "
                "WITH its reasons; reason-less scores are refused")
    if not ballot.evidence_refs or not isinstance(ballot.evidence_refs, list):
        return ("cites no evidence — every score must name the sources "
                "it rests on (evidence_refs)")
    if not isinstance(ballot.scores, dict) or not ballot.scores:
        return "carries no scores"
    unknown = [c for c in ballot.scores if c not in candidate_ids]
    if unknown:
        return f"scores name candidates outside this pass: {unknown}"
    run = ballot.run or {}
    if ballot.source_class == "MODEL_PROVIDER":
        missing = [k for k in ("provider", "model", "run_id",
                               "response_hash", "entitlement")
                   if not run.get(k)]
        if missing:
            return f"MODEL_PROVIDER ballot lacks run record fields: {missing}"
    # Dedupe is PER ROUND (cycle v2 validates each round's ballot set
    # separately): the same voter legitimately votes in both rounds.
    key = (round_no, ballot.source_class, ballot.voter, run.get("run_id"))
    if key in seen_keys:
        return f"duplicate ballot (dedupe key): {key}"
    if round_no == 2:
        if not ballot.evidence_bundle_sha256:
            return ("round-2 ballot does not carry the equalized evidence "
                    "bundle sha256 — rejected")
        if bundle_sha256 and ballot.evidence_bundle_sha256 != bundle_sha256:
            return ("round-2 ballot carries a different evidence bundle "
                    "sha256 than the equalized set — rejected")
    return None


def ballot_to_record(ballot: BallotSignal) -> dict:
    """The recorded-ballot shape cross_vote / method_cycle consume."""
    rec = {"voter": ballot.voter, "source_class": ballot.source_class,
           "scores": ballot.scores, "rationale": ballot.rationale,
           "evidence_refs": ballot.evidence_refs}
    if ballot.run:
        rec["run"] = ballot.run
    if ballot.revision_reason:
        rec["revision_reason"] = ballot.revision_reason
    if ballot.round == 2 and ballot.evidence_bundle_sha256:
        # method_cycle's stage-5 gate reads this key.
        rec["evidence_set_sha256"] = ballot.evidence_bundle_sha256
    return rec


@workflow.defn
class DelphiCycleWorkflow:
    def __init__(self) -> None:
        self._stage = "init"
        self._pass_id = ""
        self._candidate_ids: list[str] = []
        self._ballots: dict[int, list[dict]] = {1: [], 2: []}
        self._seen_keys: set = set()
        self._rejected: list[dict] = []
        self._bundle_sha256: str | None = None
        self._round1_aggregate: dict | None = None
        self._ranked_outcome: list | None = None
        self._facilitator: list[dict] = []
        self._closed: set[int] = set()
        self._round2_open = False

    # -- signals ----------------------------------------------------
    @workflow.signal
    def submit_ballot(self, ballot: BallotSignal) -> None:
        open_round = 1 if self._stage == "round1_open" else \
            2 if self._stage == "round2_open" else None
        if open_round is None:
            reason = f"no round is open (stage={self._stage})"
        else:
            reason = validate_ballot(
                ballot, round_no=open_round,
                candidate_ids=self._candidate_ids,
                bundle_sha256=self._bundle_sha256,
                seen_keys=self._seen_keys)
        if reason is not None:
            self._rejected.append({
                "voter": ballot.voter, "source_class": ballot.source_class,
                "round": ballot.round, "reason": reason})
            return
        run = ballot.run or {}
        self._seen_keys.add((ballot.round, ballot.source_class,
                             ballot.voter, run.get("run_id")))
        self._ballots[ballot.round].append(ballot_to_record(ballot))

    @workflow.signal
    def facilitator_action(self, sig: FacilitatorSignal) -> None:
        self._facilitator.append({"action": sig.action, "by": sig.by,
                                  "note": sig.note})
        if sig.action == "close_round_1":
            self._closed.add(1)
        elif sig.action == "open_round_2":
            self._round2_open = True
        elif sig.action == "close_round_2":
            self._closed.add(2)

    # -- queries ----------------------------------------------------
    @workflow.query
    def cycle_status(self) -> dict:
        per_round = {}
        for rnd, ballots in self._ballots.items():
            counts = {cls: 0 for cls in CLASSES}
            for b in ballots:
                counts[b["source_class"]] = counts.get(b["source_class"], 0) + 1
            per_round[str(rnd)] = counts
        return {"schema": "delphi-cycle-status/v1",
                "pass_id": self._pass_id,
                "stage": self._stage,
                "candidates": self._candidate_ids,
                "ballots_received": per_round,
                "rejected_ballots": self._rejected,
                "evidence_bundle_sha256": self._bundle_sha256,
                "round2_open": self._round2_open,
                "facilitator_actions": self._facilitator,
                "round1_ranked_outcome": (self._round1_aggregate or {}).get(
                    "ranked_outcome"),
                "ranked_outcome": self._ranked_outcome}

    # -- run ----------------------------------------------------------
    @workflow.run
    async def run(self, inp: CycleInput) -> dict:
        common = {"pass_id": inp.pass_brief.get("id", ""),
                  "workdir": inp.workdir}
        self._pass_id = common["pass_id"]

        self._stage = "generate"
        pass_meta = await workflow.execute_activity(
            ACT_GENERATE, {**common, "pass_brief": inp.pass_brief,
                           "evidence_sets": inp.evidence_sets,
                           "generated_at": inp.generated_at},
            start_to_close_timeout=timedelta(minutes=10))
        self._candidate_ids = [c["id"] for c in pass_meta["candidates"]]

        self._stage = "round1_open"
        await workflow.wait_condition(lambda: 1 in self._closed)

        self._stage = "cross_vote_round_1"
        round1 = await workflow.execute_activity(
            ACT_ROUND1, {**common, "pass_meta": pass_meta,
                         "panel_roles": inp.panel_roles,
                         "weights_source": inp.weights_source,
                         "ballots": self._ballots[1],
                         "generated_at": inp.generated_at},
            start_to_close_timeout=timedelta(minutes=10))
        self._round1_aggregate = round1

        self._stage = "expectations_synthesis"
        exp_synth = await workflow.execute_activity(
            ACT_EXPECT_SYNTH, {**common, "pass_meta": pass_meta,
                               "round1": round1,
                               "round1_ballots": self._ballots[1],
                               "panel_roles": inp.panel_roles,
                               "config": inp.config,
                               "recorded_expectations":
                                   inp.recorded_expectations},
            start_to_close_timeout=timedelta(minutes=10))

        self._stage = "implementation"
        impl_raw = await workflow.execute_activity(
            ACT_IMPL, {**common, "suite_specs": inp.suite_specs,
                       "candidate_ids": self._candidate_ids},
            start_to_close_timeout=timedelta(minutes=30),
            # 60s: kill-recovery latency IS the heartbeat timeout —
            # the activity heartbeats through long suites (poll loop
            # in run_implementation_suites_activity), so a dead worker
            # is detected and the stage retried within ~a minute.
            heartbeat_timeout=timedelta(seconds=60))

        self._stage = "evidence_equalization"
        equalized = await workflow.execute_activity(
            ACT_EQUALIZE, {**common, "pass_meta": pass_meta,
                           "impl_results": impl_raw,
                           "config": inp.config},
            start_to_close_timeout=timedelta(minutes=10))
        self._bundle_sha256 = equalized["evidence_sha256"]

        self._stage = "round2_gate"
        await workflow.wait_condition(lambda: self._round2_open)

        self._stage = "round2_open"
        await workflow.wait_condition(lambda: 2 in self._closed)

        self._stage = "finalize"
        slim = await workflow.execute_activity(
            ACT_FINALIZE, {**common, "pass_meta": pass_meta,
                           "panel_roles": inp.panel_roles,
                           "weights_source": inp.weights_source,
                           "config": inp.config,
                           "round1_ballots": self._ballots[1],
                           "round2_ballots": self._ballots[2],
                           "impl_results": impl_raw,
                           "recorded_expectations":
                               inp.recorded_expectations,
                           "generated_at": inp.generated_at,
                           "expectations": exp_synth["expectations"],
                           "impl_transformed": equalized["impl"],
                           "evidence_sha256": equalized["evidence_sha256"]},
            start_to_close_timeout=timedelta(minutes=10))
        self._ranked_outcome = slim["ranked_outcome"]

        self._stage = "emit_records"
        emission = await workflow.execute_activity(
            ACT_EMIT, {**common, "workflow_id": workflow.info().workflow_id,
                       "ledger_mode": inp.ledger_mode},
            start_to_close_timeout=timedelta(minutes=10))

        self._stage = "complete"
        return {"schema": "delphi-cycle-workflow-result/v1",
                "pass_id": self._pass_id,
                "stage": self._stage,
                "ranked_outcome": self._ranked_outcome,
                "evidence_bundle_sha256": self._bundle_sha256,
                "ballots_accepted": {str(k): len(v)
                                     for k, v in self._ballots.items()},
                "ballots_rejected": self._rejected,
                "cycle": slim,
                "emission": emission}
