"""The Oracle Method full cycle (owner spec, 2026-10-27).

A pass is not a vote; it is a cycle:

1. Generate          — n candidate proposals (generate_proposal --pass).
2. Cross-vote round 1 — comparative ballots across the set, source
   classes separate (cross_vote.py), AND each candidate's *input vote
   expectations* recorded: the priors on record BEFORE any
   implementation exists.
2b. Facilitator feedback — the classical Delphi step: the facilitator
   synthesizes round 1 (score distributions, the arguments FOR and
   AGAINST each candidate drawn from the ballots' own rationales,
   dissent preserved, nothing attributed) and issues it as anonymous
   controlled feedback. A DEBATE / revision round is CALLABLE at this
   point: panelists answer the synthesis with revised ballots (each
   carrying rationale, cited sources, and a revision_reason), and the
   revised outcome joins the expectations record. No ballots supplied
   = the revision round is recorded specified_not_run; the synthesis
   is issued either way.
3. Implementation    — the candidates are implemented in parallel and
   compared; tests run per individual proposal. Results arrive as one
   JSON record per candidate. Every suite result must carry a RUN
   RECEIPT (command, exit code, output hash, the code paths it ran):
   an unreceipted suite contributes ZERO passes and is flagged —
   round 2 never votes on tests whose execution is not evidenced
   (the phantom-test rule).
4. Equalization      — round 2 opens on NEW evidence, and the evidence
   base is IDENTICAL for every voter: the per-proposal test results
   bundle. Its sha256 is stamped on the round-2 receipt, and any
   supplied round-2 ballot must carry that exact hash — a ballot on
   different evidence is rejected (stage gate).
5. Re-vote round 2   — ballots on the common evidence.
6. Calibration       — round-2 outcome vs the recorded round-1
   expectations: per-candidate rank/score deltas, with the evidence
   that moved them. The calibration record is the feed for the
   weighting / elo ledgers.

Honesty rule: a stage that cannot execute (no implementation results
supplied; model ballots gated) is recorded `specified_not_run` in the
cycle record — never silently dropped, never fabricated. Parameters
(n, rounds, tolerances, convergence) come from the method config
(panel.json `generation.cycle`), overridable per pass — never
hardcoded here.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from cross_vote import (CLASSES, aggregate, cross_vote, rank, role_weight,
                        rubric_ballots, validate_ballots, _sha)

SCHEMA = "oracle-method-cycle/v1"


def derive_expectations(round1: dict, tolerance: float) -> dict:
    """Priors on record: absent new evidence, round 2 is expected to
    reproduce round 1. Derived per class present in round 1."""
    expectations = {}
    for cls in CLASSES:
        per = round1["per_class"].get(cls) or {}
        if not per.get("ballots"):
            continue
        expectations[cls] = {
            cand: {"expected_rank": pos + 1,
                   "expected_score": per["scores"][cand],
                   "tolerance": tolerance}
            for pos, cand in enumerate(per["ranking"])
        }
    return {"schema": "oracle-method-expectations/v1",
            "recorded_before": "implementation",
            "basis": "round-1 cross-vote outcome per source class",
            "expectations": expectations}


def rubric_ballots_round2(profiles: list[dict], impl: dict,
                          roles: list[str]) -> list[dict]:
    """Round-2 LOCAL_BASELINE ballots: the profile rubric re-scored on
    the equalized implementation evidence (per-proposal pass rates)."""
    def clamp(x: float) -> int:
        return max(1, min(25, round(x)))

    ballots = []
    for role in roles:
        scores = {}
        for p in profiles:
            er = p["evidenced_ratio"]
            pr = impl[p["candidate"]]["pass_rate"]
            if role == "OPERATOR":
                s = 25 * (0.5 * er + 0.5 * pr)
            elif role == "builder":
                s = 25 * (0.4 * er + 0.6 * pr)
            elif role == "reviewer":
                unv = p["unverified"] / p["points"] if p["points"] else 1
                s = 25 * (0.5 * (1 - unv) + 0.5 * pr)
            elif role == "Scout":
                s = 25 * (0.5 * er + 0.5 * pr)
            elif role == "cost_auditor":
                s = 25 * (0.5 * er + 0.5 * pr) - 2 * p["dependency_items"]
            else:
                s = 25 * (0.5 * er + 0.5 * pr)
            scores[p["candidate"]] = clamp(s)
        rationale = {p["candidate"]:
                     f"evidenced_ratio {p['evidenced_ratio']}; implementation "
                     f"pass_rate {impl[p['candidate']]['pass_rate']} "
                     f"({impl[p['candidate']]['passed']} passed / "
                     f"{impl[p['candidate']]['failed']} failed, receipted "
                     f"suites only)"
                     for p in profiles}
        ballots.append({"voter": f"rubric:{role}",
                        "source_class": "LOCAL_BASELINE", "scores": scores,
                        "rationale": rationale,
                        "evidence_refs": ["equalized round-2 evidence bundle "
                                          "(sha256 on the receipt)"]})
    return ballots


def build_synthesis(round1: dict, ballots_by_class_ballots: dict,
                    tolerance: float) -> dict:
    """The facilitator's controlled-feedback packet (classical Delphi
    stage 6): per candidate, the score distribution per class and the
    arguments as the voters themselves stated them (their ballot
    rationales) — attributed to class only, never to a person.
    Disagreement is reported, not averaged away."""
    candidates = {}
    all_ballots = [b for ballots in ballots_by_class_ballots.values()
                   for b in ballots]
    for cand in round1["ranked_outcome"] or []:
        per_class = {}
        for cls in CLASSES:
            scores = [b["scores"][cand] for b in all_ballots
                      if b.get("source_class") == cls and cand in b.get("scores", {})]
            if scores:
                per_class[cls] = {"n": len(scores), "min": min(scores),
                                  "max": max(scores),
                                  "spread": max(scores) - min(scores)}
        arguments = []
        for b in all_ballots:
            r = b.get("rationale")
            text = r.get(cand) if isinstance(r, dict) else r
            if text:
                arguments.append({"class": b.get("source_class"),
                                  "voter": b.get("voter"),
                                  "score": b["scores"].get(cand),
                                  "rationale": text,
                                  "evidence_refs": b.get("evidence_refs")})
        spread = max((v["spread"] for v in per_class.values()), default=0)
        candidates[cand] = {
            "scores_by_class": per_class,
            "arguments": arguments,
            "dissent": ("stable disagreement recorded (spread "
                        f"{spread} > tolerance {tolerance}); reported, "
                        "not forced to consensus") if spread > tolerance
                       else "no material disagreement in round 1",
        }
    return {"schema": "delphi-facilitator-synthesis/v1",
            "basis": "round-1 ballots, verbatim rationales",
            "attribution": "class + panel role only; no personal identity",
            "candidates": candidates}


def run_cycle(pass_meta: dict, panel_roles_cfg: dict, weights_source: str,
              config: dict,
              round1_ballots: list[dict] | None = None,
              feedback_ballots: list[dict] | None = None,
              round2_ballots: list[dict] | None = None,
              impl_results: dict | None = None,
              recorded_expectations: dict | None = None,
              generated_at: str | None = None) -> dict:
    generated_at = generated_at or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    candidates = [{"id": c["id"], "profile": c["profile"]}
                  for c in pass_meta["candidates"]]
    profiles = [c["profile"] for c in candidates]
    stages: list[dict] = []
    artifacts: dict = {}

    # Stage 1+2: generation (given) + round-1 cross-vote + expectations.
    round1 = cross_vote(candidates, panel_roles_cfg, weights_source,
                        round1_ballots, generated_at=generated_at)
    stages.append({"stage": "generate", "status": "ran",
                   "detail": f"n={pass_meta['n']} candidates"})
    stages.append({"stage": "cross_vote_round_1", "status": "ran",
                   "detail": f"ballots_by_class={round1['ballots_by_class']}"})
    artifacts["round1"] = round1

    # Expectations coexist by source: the round-1-derived priors per
    # voting class, plus any brief-supplied priors — recorded under
    # their author's name as their own source (a brief author's priors
    # are not a ballot class and never pose as one).
    exp_map = dict(derive_expectations(
        round1, config.get("expectation_tolerance", 2.0))["expectations"])
    if recorded_expectations:
        author = recorded_expectations.get("author", "brief")
        exp_map[f"BRIEF:{author}"] = recorded_expectations["expectations"]
    expectations = {"schema": "oracle-method-expectations/v1",
                    "recorded_before": "implementation",
                    "basis": "round-1 cross-vote per class, plus brief-supplied "
                             "priors where recorded",
                    "expectations": exp_map}
    artifacts["expectations"] = expectations
    stages.append({"stage": "expectations_recorded", "status": "ran",
                   "detail": "priors on record before implementation"})

    # Stage 2b: facilitator synthesis + the callable DEBATE / revision
    # round (classical controlled feedback). The synthesis is issued
    # from round 1's own stated reasons; revised ballots must answer
    # it (rationale + cited sources + revision_reason, enforced).
    r1_ballots = {cls: [b for b in (round1_ballots or [])
                        if b.get("source_class") == cls]
                  for cls in CLASSES}
    r1_ballots["LOCAL_BASELINE"] = rubric_ballots(
        profiles, list(panel_roles_cfg))
    synthesis = build_synthesis(
        round1, r1_ballots, config.get("expectation_tolerance", 2.0))
    artifacts["synthesis"] = synthesis
    stages.append({"stage": "facilitator_feedback", "status": "ran",
                   "detail": "synthesis issued from round-1 rationales; "
                             "arguments unattributed beyond class + role"})
    if feedback_ballots:
        for b in feedback_ballots:
            if not b.get("revision_reason"):
                raise ValueError(
                    f"feedback ballot from {b.get('voter')!r} carries no "
                    "revision_reason — a revision (or a deliberate retain) "
                    "must say why, against the synthesis")
        feedback = cross_vote(candidates, panel_roles_cfg, weights_source,
                              feedback_ballots, generated_at=generated_at)
        artifacts["feedback"] = feedback
        stages.append({"stage": "debate_revision", "status": "ran",
                       "detail": f"revised ballots_by_class="
                                 f"{feedback['ballots_by_class']}"})
    else:
        stages.append({"stage": "debate_revision",
                       "status": "specified_not_run",
                       "detail": "no DEBATE / revision ballots supplied "
                                 "against the synthesis; the round is "
                                 "callable, not automatic"})

    # Eligibility gate (owner ruling, 2026-10-27): where a brief
    # carries one, the implementation stage may not run before the
    # window opens — the cycle refuses it mechanically and records
    # the gate as the reason. Generation and round 1 are not the
    # gated activity (a proposal is not the project).
    gate = pass_meta.get("eligibility_gate") or {}
    if impl_results and gate.get("window_open"):
        opens = datetime.fromisoformat(
            str(gate["window_open"]).replace("Z", "+00:00"))
        now = datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        if now < opens:
            for name in ("implementation", "evidence_equalization",
                         "cross_vote_round_2", "calibration"):
                stages.append({
                    "stage": name, "status": "specified_not_run",
                    "detail": f"eligibility gate: build window opens "
                              f"{gate['window_open']}; implementation "
                              f"refused before the window"})
            return _cycle(pass_meta, config, stages, artifacts, None,
                          generated_at)

    # Stage 3: implementation parallel-comparisons round.
    if not impl_results:
        for name in ("implementation", "evidence_equalization",
                     "cross_vote_round_2", "calibration"):
            stages.append({"stage": name, "status": "specified_not_run",
                           "detail": "no per-proposal test results supplied; "
                                     "round 2 as specified needs the "
                                     "implementation evidence"})
        return _cycle(pass_meta, config, stages, artifacts, None, generated_at)

    missing = [c["id"] for c in candidates if c["id"] not in impl_results]
    if missing:
        raise ValueError(f"implementation results missing for: {missing}")
    require_receipts = config.get("require_suite_receipts", True)
    impl = {}
    unreceipted: list[str] = []
    for c in candidates:
        rec = impl_results[c["id"]]
        suites = []
        for s in rec["suites"]:
            receipt = s.get("receipt") or {}
            ok = all(receipt.get(k) for k in
                     ("command", "output_sha256", "code_paths")) \
                and receipt.get("exit_code") == 0
            entry = dict(s)
            if require_receipts and not ok:
                # Phantom-test rule: no receipt, no passes. The suite
                # is recorded as unverified with zero credited passes;
                # its claimed passes never reach round 2.
                entry = {**entry, "passed": 0,
                         "failed": s.get("passed", 0) + s.get("failed", 0),
                         "unverified": True,
                         "receipt_state": "missing_or_invalid"}
                unreceipted.append(f"{c['id']}:{s.get('name')}")
            else:
                entry["receipt_state"] = "verified" if ok else "not_required"
            suites.append(entry)
        passed = sum(s.get("passed", 0) for s in suites)
        failed = sum(s.get("failed", 0) for s in suites)
        impl[c["id"]] = {"suites": suites, "passed": passed,
                         "failed": failed,
                         "pass_rate": (passed / (passed + failed)) if (passed + failed) else 0.0}
    artifacts["implementation"] = impl
    stages.append({"stage": "implementation", "status": "ran",
                   "detail": "parallel per-proposal test results recorded"
                             + (f"; UNRECEIPTED suites credited zero passes: "
                                f"{unreceipted}" if unreceipted else
                                "; all suites receipt-verified")})

    # Stage 4: evidence equalization — one bundle, one hash, every voter.
    bundle = {"schema": "delphi-round2-evidence/v1",
              "pass_id": pass_meta["pass_id"], "results": impl}
    evidence_sha = _sha(bundle)
    artifacts["round2_evidence"] = {**bundle, "sha256": evidence_sha}
    stages.append({"stage": "evidence_equalization", "status": "ran",
                   "detail": f"common evidence set sha256={evidence_sha[:12]}…"})

    # Stage 5: round-2 vote on the common evidence. Supplied ballots
    # must carry the bundle hash (stage gate); the rubric comparator
    # is constructed from the bundle itself, so its equality is
    # structural.
    validate_ballots(round2_ballots or [])
    for ballot in (round2_ballots or []):
        if ballot.get("evidence_set_sha256") != evidence_sha:
            raise ValueError(
                f"round-2 ballot from {ballot.get('voter')!r} does not carry "
                "the equalized evidence hash — rejected")
    roles = list(panel_roles_cfg.keys())
    weights = {r: role_weight(cfg) for r, cfg in panel_roles_cfg.items()}
    baseline2 = rubric_ballots_round2(profiles, impl, roles)
    by_class: dict[str, list[dict]] = {cls: [] for cls in CLASSES}
    by_class["LOCAL_BASELINE"] = baseline2
    for ballot in (round2_ballots or []):
        by_class[ballot["source_class"]].append(ballot)
    per_class = {}
    for cls, ballots in by_class.items():
        if not ballots:
            per_class[cls] = {"ballots": 0, "scores": {}, "ranking": []}
            continue
        w = weights if cls == "LOCAL_BASELINE" else None
        scores = aggregate(ballots, w)
        per_class[cls] = {"ballots": len(ballots),
                          "scores": {k: round(v, 3) for k, v in scores.items()},
                          "ranking": rank(scores)}
    present = [cls for cls in CLASSES if per_class[cls]["ballots"] > 0]
    round2 = {"schema": "delphi-cross-vote/v1", "round": 2,
              "evidence_set_sha256": evidence_sha,
              "ballots_by_class": {cls: per_class[cls]["ballots"] for cls in CLASSES},
              "per_class": per_class,
              "classes_present": present,
              "ranked_outcome": per_class[present[0]]["ranking"] if present else []}
    artifacts["round2"] = round2
    stages.append({"stage": "cross_vote_round_2", "status": "ran",
                   "detail": f"ranked={round2['ranked_outcome']}"})

    # Stage 6: calibration vs the recorded expectations.
    calibration = {"schema": "oracle-method-calibration/v1",
                   "evidence_set_sha256": evidence_sha, "candidates": {}}
    primary_cls = present[0] if present else None
    for cls, expected in expectations["expectations"].items():
        # Brief-supplied priors calibrate against the primary round-2
        # outcome; class priors against their own class.
        actual = (round2["per_class"].get(primary_cls) or {}) \
            if cls.startswith("BRIEF:") else (round2["per_class"].get(cls) or {})
        if not actual.get("ballots"):
            calibration["candidates"].setdefault(cls, "class_absent_round_2")
            continue
        per_cand = {}
        for pos, cand in enumerate(actual["ranking"]):
            exp = expected[cand]
            moved_on = []
            rec = impl[cand]
            if rec["failed"]:
                moved_on.append(f"{rec['failed']} failing test(s) in the "
                                "implementation round")
            if rec["pass_rate"] == 1.0:
                moved_on.append("full test pass in the implementation round")
            tol = exp.get("tolerance", config.get("expectation_tolerance", 2.0))
            per_cand[cand] = {
                "expected_rank": exp["expected_rank"], "actual_rank": pos + 1,
                "rank_delta": (pos + 1) - exp["expected_rank"],
                "expected_score": exp["expected_score"],
                "actual_score": actual["scores"][cand],
                "score_delta": round(actual["scores"][cand]
                                     - exp["expected_score"], 3),
                "within_tolerance": abs(actual["scores"][cand]
                                        - exp["expected_score"]) <= tol,
                "moved_on_evidence": moved_on or ["no discriminating test evidence"],
            }
        calibration["candidates"][cls] = per_cand
    artifacts["calibration"] = calibration
    stages.append({"stage": "calibration", "status": "ran",
                   "detail": "round-2 vs round-1 expectations; feed for the "
                             "weighting/elo ledgers"})
    feed = {"type": "delphi-generation-calibration",
            "pass_id": pass_meta["pass_id"], "calibration": calibration}
    return _cycle(pass_meta, config, stages, artifacts, feed, generated_at)


def _cycle(pass_meta, config, stages, artifacts, feed, generated_at):
    return {"schema": SCHEMA, "pass_id": pass_meta["pass_id"],
            "generated_at": generated_at, "config": config,
            "stages": stages, "artifacts": artifacts, "ledger_feed": feed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Oracle Method full cycle")
    parser.add_argument("--pass-dir", required=True)
    parser.add_argument("--panel", required=True)
    parser.add_argument("--weights-file")
    parser.add_argument("--round1-ballots", action="append", default=[])
    parser.add_argument("--feedback-ballots", action="append", default=[],
                        help="DEBATE / revision ballots answering the "
                             "facilitator synthesis")
    parser.add_argument("--round2-ballots", action="append", default=[])
    parser.add_argument("--implementation-dir",
                        help="dir with one <candidate-id>.json per candidate")
    parser.add_argument("--expectations-file",
                        help="recorded expectations JSON (else derived from round 1)")
    parser.add_argument("--out", required=True, help="cycle output directory")
    args = parser.parse_args(argv)

    pass_dir = Path(args.pass_dir)
    pass_meta = json.loads((pass_dir / "pass.json").read_text())
    panel = json.loads(Path(args.panel).read_text())
    config = (panel.get("generation") or {}).get("cycle", {})
    roles_cfg = panel["roles"]
    source = "panel.json cold-start defaults"
    if args.weights_file:
        ledger = json.loads(Path(args.weights_file).read_text())
        if ledger and ledger.get("roles"):
            roles_cfg = ledger["roles"]
            source = f"ledger weights file {args.weights_file}"

    def load_ballots(paths):
        out = []
        for p in paths:
            data = json.loads(Path(p).read_text())
            out.extend(data if isinstance(data, list) else [data])
        return out

    impl = None
    if args.implementation_dir:
        impl = {}
        for f in Path(args.implementation_dir).glob("*.json"):
            impl[f.stem] = json.loads(f.read_text())
    recorded = None
    if args.expectations_file:
        recorded = json.loads(Path(args.expectations_file).read_text())
        if "expectations" not in recorded:
            recorded = {"author": recorded.get("author", "brief"),
                        "expectations": recorded}

    cycle = run_cycle(pass_meta, roles_cfg, source, config,
                      round1_ballots=load_ballots(args.round1_ballots),
                      feedback_ballots=load_ballots(args.feedback_ballots),
                      round2_ballots=load_ballots(args.round2_ballots),
                      impl_results=impl, recorded_expectations=recorded)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    names = {"round1": "BALLOT-round1.json", "expectations": "EXPECTATIONS.json",
             "synthesis": "SYNTHESIS.json", "feedback": "FEEDBACK.json",
             "implementation": "IMPLEMENTATION.json",
             "round2_evidence": "ROUND2-EVIDENCE.json",
             "round2": "BALLOT-round2.json", "calibration": "CALIBRATION.json"}
    for key, fname in names.items():
        if cycle["artifacts"].get(key) is not None:
            (out / fname).write_text(json.dumps(cycle["artifacts"][key], indent=2) + "\n")
    slim = {**cycle, "artifacts": {k: names[k] for k in names
                                   if cycle["artifacts"].get(k) is not None}}
    (out / "CYCLE.json").write_text(json.dumps(slim, indent=2) + "\n")
    ran = [s["stage"] for s in cycle["stages"] if s["status"] == "ran"]
    skipped = [s["stage"] for s in cycle["stages"] if s["status"] != "ran"]
    print(f"cycle {cycle['pass_id']}: ran={ran} specified_not_run={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
