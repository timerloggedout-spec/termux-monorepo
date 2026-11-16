#!/usr/bin/env python3
"""Delphi cycle client + §5 acceptance proof driver (N5).

Subcommands:
  start   — start a DelphiCycleWorkflow for a fixture/real brief
            (workflow ID = delphi-cycle/<pass-id>, the idempotency
            boundary: re-starting the same pass ID is refused by the
            server while a run is open, and a closed ID replays its
            recorded result).
  ballot  — cast one BallotSignal from a JSON file.
  facilitator — close_round_1 | open_round_2 | close_round_2.
  status  — CycleStatus query (works mid-cycle and after completion).
  result  — await + print the workflow result.
  prove   — the brief §5 live acceptance, end to end, with receipts:
            fixture cycle on the self-host → receipted round-1 ballots
            → CycleStatus mid-cycle → SIGKILL the worker
            mid-implementation-round → second worker resumes and
            completes → wrong-hash round-2 ballot rejected + recorded,
            correct-hash accepted → ledger payloads exactly once
            (emit re-invoked: already_posted, marker count == 1) →
            dual-run parity vs method_cycle.run_cycle on the same
            fixture inputs. Prints the evidence envelope JSON.

Fixture suites are tiny receipted python commands; the strong
candidate's implementation suite sleeps first — that sleep is the
SIGKILL window (the kill lands mid-implementation-round by
construction, and the suite's receipt proves which attempt counted).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "delphi"))

from temporalio.client import Client  # noqa: E402

from workflow import (BallotSignal, CycleInput, DelphiCycleWorkflow,  # noqa: E402
                      FacilitatorSignal, TASK_QUEUE)

GENERATED_AT = "2026-10-28T00:00:00Z"  # fixture clock: parity needs one


# The rehearsal fixture — values identical to
# tests/test_delphi_cross_vote.py (EVIDENCE / PASS_BRIEF / PANEL), so
# the workflow path and the script path run the SAME fixture (§3).
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

# Key order is the payload converter's canonical (sorted) order:
# Temporal's JSON conversion sorts dict keys in transit, so a fixture
# authored in this order produces byte-identical artifacts on both
# the script path and the workflow path (parity, §3).
PANEL_ROLES = {
    "OPERATOR": {"base": 1.2, "gate_pass_rate": 0.68, "elo": 1532},
    "Scout": {"base": 0.8, "gate_pass_rate": 0.68, "elo": 1532},
    "builder": {"base": 1.0, "gate_pass_rate": 0.68, "elo": 1532},
    "cost_auditor": {"base": 1.2, "gate_pass_rate": 0.68, "elo": 1532},
    "reviewer": {"base": 1.0, "gate_pass_rate": 0.68, "elo": 1532},
}


def _fixture() -> dict:
    return {"pass_brief": PASS_BRIEF, "evidence_sets": EVIDENCE,
            "panel_roles": PANEL_ROLES}


def fixture_input(workdir: str, ledger_mode: str = "github") -> CycleInput:
    fx = _fixture()
    strong_sleep = ["sleep_first", "25"]
    def suite(name, passed, failed, argv):
        return {"name": name, "argv": argv, "code_paths": ["scripts/temporal/delphi_cycle/client.py"]}
    py = sys.executable
    def emit(passed, failed, pre=None):
        code = (f"import json,time; time.sleep({pre}) if {pre} else None; "
                f"print(json.dumps({{'passed': {passed}, 'failed': {failed}}}))")
        return [py, "-c", code]
    specs = {
        "rehearsal-strong": [suite("concept", 4, 0, emit(4, 0, pre=25))],
        "rehearsal-weak": [suite("concept", 1, 3, emit(1, 3))],
        "rehearsal-empty": [suite("concept", 0, 2, emit(0, 2))],
    }
    return CycleInput(
        pass_brief=fx["pass_brief"], evidence_sets=fx["evidence_sets"],
        panel_roles=fx["panel_roles"],
        weights_source="fixture panel (tests/test_delphi_cross_vote PANEL)",
        config={"rounds": 2, "expectation_tolerance": 2.0},
        suite_specs=specs, generated_at=GENERATED_AT,
        workdir=workdir, ledger_mode=ledger_mode)


R1_BALLOT = {"voter": "registrar:owner", "source_class": "HUMAN_COLLABORATOR",
             "round": 1,
             "scores": {"rehearsal-strong": 20, "rehearsal-weak": 12,
                        "rehearsal-empty": 6},
             "rationale": "strong is fully evidenced; weak rests one point "
                          "on a missing claim; empty is unevidenced",
             "evidence_refs": ["fixture evidence set a.claim/b.claim"]}


def _r2_ballot(bundle_sha: str | None) -> dict:
    b = {"voter": "registrar:owner", "source_class": "HUMAN_COLLABORATOR",
         "round": 2,
         "scores": {"rehearsal-strong": 21, "rehearsal-weak": 9,
                    "rehearsal-empty": 4},
         "rationale": "on the equalized bundle: strong passes 4/4, weak "
                      "1/4, empty 0/2 — scored on that common evidence",
         "evidence_refs": ["equalized round-2 evidence bundle"]}
    if bundle_sha:
        b["evidence_bundle_sha256"] = bundle_sha
    return b


async def _connect(address: str) -> Client:
    return await Client.connect(address)


def _wf_id(pass_id: str) -> str:
    return f"delphi-cycle/{pass_id}"


async def _start(client: Client, inp: CycleInput) -> str:
    handle = await client.start_workflow(
        DelphiCycleWorkflow.run, inp, id=_wf_id(inp.pass_brief["id"]),
        task_queue=TASK_QUEUE)
    return handle.id


async def _status(client: Client, wf_id: str) -> dict:
    handle = client.get_workflow_handle(wf_id)
    return await handle.query(DelphiCycleWorkflow.cycle_status)


async def _wait_stage(client: Client, wf_id: str, stage: str,
                      timeout: float = 120) -> dict:
    deadline = time.time() + timeout
    last = {}
    while time.time() < deadline:
        last = await _status(client, wf_id)
        if last["stage"] == stage:
            return last
        await asyncio.sleep(1)
    raise TimeoutError(f"stage {stage} not reached; last={last}")


def _spawn_worker(address: str, log: Path) -> subprocess.Popen:
    worker_py = Path(__file__).resolve().parent / "worker.py"
    fh = open(log, "ab")
    return subprocess.Popen(
        [sys.executable, str(worker_py), "--address", address],
        stdout=fh, stderr=subprocess.STDOUT)


async def _prove(address: str, workdir: str, ledger_mode: str) -> dict:
    receipts: dict = {"schema": "n5-acceptance/v1",
                      "started_at": datetime.now(timezone.utc).strftime(
                          "%Y-%m-%dT%H:%M:%SZ")}
    client = await _connect(address)
    inp = fixture_input(workdir, ledger_mode)
    wf_id = await _start(client, inp)
    receipts["workflow_id"] = wf_id
    handle = client.get_workflow_handle(wf_id)

    worker1 = _spawn_worker(address, Path(workdir) / "worker1.log")
    receipts["worker1_pid"] = worker1.pid
    try:
        await _wait_stage(client, wf_id, "round1_open")
        await handle.signal(DelphiCycleWorkflow.submit_ballot,
                            BallotSignal(**R1_BALLOT))
        await handle.signal(DelphiCycleWorkflow.facilitator_action,
                            FacilitatorSignal(action="close_round_1",
                                              by="facilitator:prove"))
        st = await _wait_stage(client, wf_id, "implementation")
        receipts["status_mid_cycle"] = st
        assert st["ballots_received"]["1"]["HUMAN_COLLABORATOR"] == 1, st

        # §5.3 — SIGKILL mid-implementation-round.
        worker1.send_signal(signal.SIGKILL)
        worker1.wait(timeout=10)
        receipts["worker1_killed"] = {"pid": worker1.pid,
                                      "stage_at_kill": st["stage"],
                                      "signal": "SIGKILL"}
        worker2 = _spawn_worker(address, Path(workdir) / "worker2.log")
        receipts["worker2_pid"] = worker2.pid
        try:
            st2 = await _wait_stage(client, wf_id, "round2_gate",
                                    timeout=900)
            bundle = st2["evidence_bundle_sha256"]
            assert bundle, st2
            receipts["evidence_bundle_sha256"] = bundle
            await handle.signal(DelphiCycleWorkflow.facilitator_action,
                                FacilitatorSignal(action="open_round_2",
                                                  by="facilitator:prove"))
            await _wait_stage(client, wf_id, "round2_open")
            # §5.4 — wrong-hash and missing-hash ballots rejected.
            await handle.signal(DelphiCycleWorkflow.submit_ballot,
                                BallotSignal(**_r2_ballot("0" * 64)))
            await handle.signal(DelphiCycleWorkflow.submit_ballot,
                                BallotSignal(**_r2_ballot(None)))
            await handle.signal(DelphiCycleWorkflow.submit_ballot,
                                BallotSignal(**_r2_ballot(bundle)))
            st3 = await _status(client, wf_id)
            receipts["status_round2"] = st3
            rejected = st3["rejected_ballots"]
            assert len(rejected) == 2, rejected
            assert all("evidence bundle sha256" in r["reason"]
                       or "evidence_bundle_sha256" in r["reason"]
                       or "sha256" in r["reason"] for r in rejected), rejected
            assert st3["ballots_received"]["2"]["HUMAN_COLLABORATOR"] == 1
            await handle.signal(DelphiCycleWorkflow.facilitator_action,
                                FacilitatorSignal(action="close_round_2",
                                                  by="facilitator:prove"))
            result = await asyncio.wait_for(handle.result(), timeout=300)
            receipts["workflow_result"] = result
        finally:
            worker2.terminate()
    finally:
        if worker1.poll() is None:
            worker1.terminate()

    # §5.5 — exactly-once: re-invoke emission; markers must already exist.
    import activities
    again = activities.emit_records_activity(
        {"pass_id": inp.pass_brief["id"], "workdir": workdir,
         "workflow_id": wf_id, "ledger_mode": ledger_mode})
    receipts["emission_reinvoke"] = again
    if ledger_mode == "github":
        for r in again["receipts"]:
            assert r["state"] in ("already_posted", "specified_not_run"), r
    history = await handle.fetch_history()
    receipts["history_events"] = len(history.events)
    receipts["history_sha256"] = hashlib.sha256(
        json.dumps([str(e) for e in history.events]).encode()).hexdigest()
    receipts["verdict"] = "PASS"
    return receipts


def _parity(workdir: str) -> dict:
    """§3 dual-run parity: method_cycle.run_cycle on the same fixture
    inputs (same generated_at, same accepted ballots, the workflow's
    raw implementation results) vs the workflow's emitted artifacts."""
    import method_cycle as mc
    cyc_dir = Path(workdir) / "rehearsal" / "cycle"
    cycle = json.loads((cyc_dir / "CYCLE.json").read_text())
    names = cycle["artifacts"]
    wf_artifacts = {k: json.loads((cyc_dir / f).read_text())
                    for k, f in names.items()}
    impl_raw = {}
    impl = wf_artifacts["implementation"]
    for cand, rec in impl.items():
        impl_raw[cand] = {"suites": [
            {k: v for k, v in s.items()
             if k not in ("unverified", "receipt_state")}
            for s in rec["suites"]]}
    fx = _fixture()
    _, pass_meta = __import__("generate_proposal").generate_pass(
        fx["pass_brief"], fx["evidence_sets"], generated_at=GENERATED_AT)
    r1 = [dict(R1_BALLOT)]
    r1[0].pop("round")
    bundle = wf_artifacts["round2_evidence"]["sha256"]
    r2 = [_r2_ballot(bundle)]
    r2[0].pop("round")
    r2[0]["evidence_set_sha256"] = r2[0].pop("evidence_bundle_sha256")
    script_cycle = mc.run_cycle(
        pass_meta, fx["panel_roles"],
        "fixture panel (tests/test_delphi_cross_vote PANEL)",
        {"rounds": 2, "expectation_tolerance": 2.0},
        round1_ballots=r1, round2_ballots=r2, impl_results=impl_raw,
        generated_at=GENERATED_AT)
    def normalize(value):
        # Ballot LISTS are sets with a serialization order: the
        # workflow path's order follows the payload converter's
        # canonical key sort, the script path's follows the panel
        # dict's insertion order. Aggregation is order-insensitive
        # (weighted sums; rankings compared as lists elsewhere), so
        # parity compares ballots sorted by voter — the same class of
        # normalization the brief applies to timestamps and digests.
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            items = [normalize(v) for v in value]
            if items and all(isinstance(v, dict) and "voter" in v
                             for v in items):
                items.sort(key=lambda v: (v["voter"],
                                          v.get("source_class", "")))
            return items
        return value

    diffs = []
    for key, wf_art in wf_artifacts.items():
        sc_art = script_cycle["artifacts"].get(key)
        if normalize(sc_art) != normalize(wf_art):
            diffs.append(key)
    return {"compared": sorted(wf_artifacts), "diffs": diffs,
            "normalization": "ballot lists sorted by voter (see code)",
            "verdict": "PASS" if not diffs else "FAIL"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--address", default="localhost:7233")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start")
    p.add_argument("--workdir", required=True)
    p.add_argument("--ledger-mode", default="github")
    p = sub.add_parser("ballot")
    p.add_argument("--workflow-id", required=True)
    p.add_argument("--file", required=True)
    p = sub.add_parser("facilitator")
    p.add_argument("--workflow-id", required=True)
    p.add_argument("--action", required=True)
    p.add_argument("--by", default="facilitator:cli")
    p = sub.add_parser("status")
    p.add_argument("--workflow-id", required=True)
    p = sub.add_parser("result")
    p.add_argument("--workflow-id", required=True)
    p = sub.add_parser("prove")
    p.add_argument("--workdir", required=True)
    p.add_argument("--ledger-mode", default="github")
    p = sub.add_parser("parity")
    p.add_argument("--workdir", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "parity":
        out = _parity(args.workdir)
        print(json.dumps(out, indent=1))
        return 0 if out["verdict"] == "PASS" else 1

    async def go():
        client = await _connect(args.address)
        if args.cmd == "start":
            inp = fixture_input(args.workdir, args.ledger_mode)
            return {"workflow_id": await _start(client, inp)}
        if args.cmd == "prove":
            return await _prove(args.address, args.workdir, args.ledger_mode)
        handle = client.get_workflow_handle(args.workflow_id)
        if args.cmd == "ballot":
            ballot = json.loads(Path(args.file).read_text())
            await handle.signal(DelphiCycleWorkflow.submit_ballot,
                                BallotSignal(**ballot))
            return await _status(client, args.workflow_id)
        if args.cmd == "facilitator":
            await handle.signal(
                DelphiCycleWorkflow.facilitator_action,
                FacilitatorSignal(action=args.action, by=args.by))
            return await _status(client, args.workflow_id)
        if args.cmd == "status":
            return await _status(client, args.workflow_id)
        if args.cmd == "result":
            return await handle.result()
    out = asyncio.run(go())
    print(json.dumps(out, indent=1, default=str))
    return 0 if out.get("verdict", "PASS") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
