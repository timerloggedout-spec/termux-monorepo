"""Stage activities for DelphiCycleWorkflow — wrappers, not rewrites.

Every activity calls the cycle machinery of record in scripts/delphi/
(generate_proposal.generate_pass, cross_vote.cross_vote,
method_cycle.{derive_expectations, build_synthesis, run_cycle}) or
executes receipted work itself (implementation suites, ledger
emission). No cycle semantics are re-implemented here; the one
transform restated is run_cycle's phantom-rule application in
`apply_phantom_rule`, pinned field-for-field against run_cycle by
tests/test_delphi_cycle.py and by finalize_cycle_activity's internal
parity assertion on every live run.

Ledger emission (emit_records_activity): payloads are built here,
in-activity; the workflow carries only digests. Routes resolve by
EXACT issue title (ops/delphi/ledgers.json registry semantics, PR
#1833 — never label+found[0]); posting goes through the fleet PAT
helper (names-only credentials). Idempotency key = workflow ID +
stage, embedded as an HTML marker in each payload; a retried activity
finds its marker already on the ledger and does not post twice.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from temporalio import activity

REPO_ROOT = Path(__file__).resolve().parents[3]
DELPHI_DIR = REPO_ROOT / "scripts" / "delphi"
if str(DELPHI_DIR) not in sys.path:
    sys.path.insert(0, str(DELPHI_DIR))

import cross_vote as cv  # noqa: E402
import method_cycle as mc  # noqa: E402
from generate_proposal import generate_pass  # noqa: E402

GH_HELPER = os.environ.get(
    "DELPHI_CYCLE_GH_HELPER",
    str(Path.home() / "workspace/custom-connectors/custom.github-pat/bin/github_pat.py"))
REPO = "timerloggedout-spec/termux-monorepo"
LEDGER_TITLES = {"generation": "Delphi outcome ledger",
                 "weights": "Delphi panel weights ledger"}


def _sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _cycle_dir(workdir: str, pass_id: str) -> Path:
    d = Path(workdir) / pass_id / "cycle"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------- stages

@activity.defn(name="generate_pass_activity")
def generate_pass_activity(args: dict) -> dict:
    """Stage: generate — n candidate proposals (generate_proposal)."""
    docs_by_dir, pass_meta = generate_pass(
        args["pass_brief"], args["evidence_sets"],
        generated_at=args["generated_at"] or None)
    out = Path(args["workdir"]) / args["pass_id"]
    for dirname, docs in docs_by_dir.items():
        sub = out / dirname
        sub.mkdir(parents=True, exist_ok=True)
        for name, text in docs.items():
            (sub / name).write_text(text)
    (out / "pass.json").write_text(json.dumps(pass_meta, indent=2) + "\n")
    return pass_meta


@activity.defn(name="cross_vote_round1_activity")
def cross_vote_round1_activity(args: dict) -> dict:
    """Stage: cross-vote round 1 (cross_vote.cross_vote, verbatim)."""
    candidates = [{"id": c["id"], "profile": c["profile"]}
                  for c in args["pass_meta"]["candidates"]]
    receipt = cv.cross_vote(candidates, args["panel_roles"],
                            args["weights_source"], args["ballots"],
                            generated_at=args["generated_at"] or None)
    receipt["pass_id"] = args["pass_id"]
    return receipt


@activity.defn(name="expectations_synthesis_activity")
def expectations_synthesis_activity(args: dict) -> dict:
    """Stages: expectations (recorded BEFORE implementation) +
    facilitator synthesis — method_cycle's own helpers, assembled
    exactly as run_cycle assembles them."""
    config = args["config"]
    tol = config.get("expectation_tolerance", 2.0)
    exp_map = dict(mc.derive_expectations(args["round1"], tol)["expectations"])
    if args.get("recorded_expectations"):
        recorded = args["recorded_expectations"]
        author = recorded.get("author", "brief")
        exp_map[f"BRIEF:{author}"] = recorded["expectations"]
    expectations = {"schema": "oracle-method-expectations/v1",
                    "recorded_before": "implementation",
                    "basis": "round-1 cross-vote per class, plus brief-supplied "
                             "priors where recorded",
                    "expectations": exp_map}
    profiles = [c["profile"] for c in args["pass_meta"]["candidates"]]
    r1_ballots = {cls: [b for b in args["round1_ballots"]
                        if b.get("source_class") == cls]
                  for cls in cv.CLASSES}
    r1_ballots["LOCAL_BASELINE"] = cv.rubric_ballots(
        profiles, list(args["panel_roles"]))
    synthesis = mc.build_synthesis(args["round1"], r1_ballots, tol)
    return {"expectations": expectations, "synthesis": synthesis}


@activity.defn(name="run_implementation_suites_activity")
def run_implementation_suites_activity(args: dict) -> dict:
    """Stage: implementation — per-candidate receipted suites.

    Each suite runs its argv and must print a JSON summary
    {"passed": n, "failed": n} as its last stdout line. The receipt
    (command, exit code, output sha256, code paths) is stamped here;
    whether it COUNTS is the phantom rule, applied in equalize —
    exactly as run_cycle applies it. A suite that cannot run at all
    is recorded with exit_code -1 and no valid receipt (zero credit),
    never fabricated.
    """
    workdir = Path(args["workdir"]) / args["pass_id"] / "suites"
    workdir.mkdir(parents=True, exist_ok=True)
    results: dict = {}
    for cand in args["candidate_ids"]:
        suites = []
        for spec in args["suite_specs"].get(cand, []):
            argv = [str(a) for a in spec["argv"]]
            try:
                # Poll loop: heartbeat through long suites so a live
                # worker is never mistaken for a dead one (and a dead
                # one is detected within the heartbeat timeout).
                proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True,
                                        cwd=str(workdir))
                deadline = spec.get("timeout_secs", 600)
                waited = 0.0
                while proc.poll() is None:
                    if waited >= deadline:
                        proc.kill()
                        raise TimeoutError(
                            f"suite exceeded {deadline}s: {argv}")
                    activity.heartbeat(f"{cand}:{spec['name']} running")
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
                    waited += 5
                stdout, stderr = proc.communicate()
                output = (stdout or "") + (stderr or "")
                exit_code = proc.returncode
            except Exception as exc:  # missing binary, timeout, …
                output = f"suite runner error: {exc}"
                exit_code = -1
            summary = {}
            for line in reversed((output or "").strip().splitlines()):
                try:
                    parsed = json.loads(line)
                except Exception:
                    continue
                if isinstance(parsed, dict) and "passed" in parsed:
                    summary = parsed
                    break
            suites.append({
                "name": spec["name"],
                "passed": int(summary.get("passed", 0)),
                "failed": int(summary.get("failed", 0)),
                "receipt": {
                    "command": " ".join(argv),
                    "exit_code": exit_code,
                    "output_sha256": hashlib.sha256(
                        (output or "").encode()).hexdigest(),
                    "code_paths": spec.get("code_paths", []),
                }})
            activity.heartbeat(f"{cand}:{spec['name']}")
        results[cand] = {"suites": suites}
    return results


def apply_phantom_rule(impl_results: dict, candidate_ids: list[str],
                       config: dict) -> tuple[dict, list[str]]:
    """run_cycle stage 3's transform, restated once: an unreceipted
    suite (missing command/output hash/code paths, or nonzero exit)
    contributes ZERO passes and is flagged unverified."""
    require_receipts = config.get("require_suite_receipts", True)
    impl: dict = {}
    unreceipted: list[str] = []
    for cand in candidate_ids:
        rec = impl_results[cand]
        suites = []
        for s in rec["suites"]:
            receipt = s.get("receipt") or {}
            ok = all(receipt.get(k) for k in
                     ("command", "output_sha256", "code_paths")) \
                and receipt.get("exit_code") == 0
            entry = dict(s)
            if require_receipts and not ok:
                entry = {**entry, "passed": 0,
                         "failed": s.get("passed", 0) + s.get("failed", 0),
                         "unverified": True,
                         "receipt_state": "missing_or_invalid"}
                unreceipted.append(f"{cand}:{s.get('name')}")
            else:
                entry["receipt_state"] = "verified" if ok else "not_required"
            suites.append(entry)
        passed = sum(s.get("passed", 0) for s in suites)
        failed = sum(s.get("failed", 0) for s in suites)
        impl[cand] = {"suites": suites, "passed": passed, "failed": failed,
                      "pass_rate": (passed / (passed + failed))
                      if (passed + failed) else 0.0}
    return impl, unreceipted


@activity.defn(name="equalize_activity")
def equalize_activity(args: dict) -> dict:
    """Stage: evidence equalization — one bundle, one hash (run_cycle
    stage 4): the phantom-transformed implementation results, stamped
    with their sha256. Round 2 votes on exactly this set."""
    candidate_ids = [c["id"] for c in args["pass_meta"]["candidates"]]
    missing = [c for c in candidate_ids if c not in args["impl_results"]]
    if missing:
        raise ValueError(f"implementation results missing for: {missing}")
    impl, unreceipted = apply_phantom_rule(
        args["impl_results"], candidate_ids, args["config"])
    bundle = {"schema": "delphi-round2-evidence/v1",
              "pass_id": args["pass_id"], "results": impl}
    return {"impl": impl, "unreceipted": unreceipted,
            "evidence_sha256": _sha(bundle)}


@activity.defn(name="finalize_cycle_activity")
def finalize_cycle_activity(args: dict) -> dict:
    """Stages: round-2 vote + calibration, BY method_cycle.run_cycle
    itself — the implementation of record. Before trusting it, assert
    its internal artifacts match the staged activities' outputs
    (expectations, phantom-transformed implementation, bundle hash):
    any divergence is a defect and fails the cycle loudly.

    Writes the pass-record artifact files (method_cycle.main shapes)
    to the workdir and returns the slim cycle projection."""
    cycle = mc.run_cycle(
        args["pass_meta"], args["panel_roles"], args["weights_source"],
        args["config"], round1_ballots=args["round1_ballots"],
        round2_ballots=args["round2_ballots"],
        impl_results=args["impl_results"],
        recorded_expectations=args.get("recorded_expectations"),
        generated_at=args["generated_at"] or None)
    art = cycle["artifacts"]
    assert art["expectations"] == args["expectations"], \
        "parity defect: staged expectations diverge from run_cycle"
    assert art["implementation"] == args["impl_transformed"], \
        "parity defect: staged phantom transform diverges from run_cycle"
    assert art["round2_evidence"]["sha256"] == args["evidence_sha256"], \
        "parity defect: staged bundle hash diverges from run_cycle"
    names = {"round1": "BALLOT-round1.json",
             "expectations": "EXPECTATIONS.json",
             "synthesis": "SYNTHESIS.json", "feedback": "FEEDBACK.json",
             "implementation": "IMPLEMENTATION.json",
             "round2_evidence": "ROUND2-EVIDENCE.json",
             "round2": "BALLOT-round2.json",
             "calibration": "CALIBRATION.json"}
    out = _cycle_dir(args["workdir"], args["pass_id"])
    for key, fname in names.items():
        if art.get(key) is not None:
            (out / fname).write_text(json.dumps(art[key], indent=2) + "\n")
    slim = {**cycle, "artifacts": {k: names[k] for k in names
                                   if art.get(k) is not None}}
    (out / "CYCLE.json").write_text(json.dumps(slim, indent=2) + "\n")
    return {"cycle_file": str(out / "CYCLE.json"),
            "stages": cycle["stages"],
            "ranked_outcome": (art.get("round2") or {}).get(
                "ranked_outcome") or (art.get("round1") or {}).get(
                "ranked_outcome"),
            "ledger_feed": cycle["ledger_feed"],
            "artifact_sha256": {k: _sha(art[k]) for k in names
                                if art.get(k) is not None}}


# ---------------------------------------------------------------- ledger

def _gh(method: str, path: str, body: dict | None = None):
    if method == "GET":
        cmd = [GH_HELPER, "get", path]
    else:
        cmd = [GH_HELPER, "api", method, path]
        if body is not None:
            cmd.append(json.dumps(body))
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"PAT helper {method} {path} failed: "
                           f"{out.stdout[:300]} {out.stderr[:200]}")
    return json.loads(out.stdout)


def resolve_issue_by_title(title: str) -> int:
    """Exact-title resolution (PR #1833 semantics): search, then keep
    only issues whose title matches EXACTLY; refuse ambiguity."""
    from urllib.parse import quote
    q = quote(f'repo:{REPO} in:title "{title}"')
    hits = _gh("GET", f"/search/issues?q={q}&per_page=10").get("items", [])
    exact = [h for h in hits if h.get("title") == title]
    if len(exact) != 1:
        raise RuntimeError(
            f"title resolution for {title!r}: {len(exact)} exact matches")
    return exact[0]["number"]


def _already_posted(issue: int, marker: str) -> dict | None:
    # Newest first, paged: the ledgers are long, and this run's marker
    # — the only one that can exist — is always among the newest.
    for page in range(1, 11):
        comments = _gh("GET", f"/repos/{REPO}/issues/{issue}/comments"
                              f"?per_page=100&page={page}"
                              "&sort=created&direction=desc")
        for c in comments:
            if marker in (c.get("body") or ""):
                return {"comment_id": c["id"]}
        if len(comments) < 100:
            return None
    return None


@activity.defn(name="emit_records_activity")
def emit_records_activity(args: dict) -> dict:
    """Stage: ledger emission — ballot + calibration payloads to the
    Delphi ledgers, exactly once per (workflow, stage).

    record_only mode (tests): payloads are built and written to the
    workdir, nothing is posted. github mode: each payload carries the
    registry marker for its ledger kind plus the idempotency marker
    `<!-- n5-emit:<workflow_id>:<stage> -->`; before posting, the
    ledger is scanned for that marker — a retry finds it and reports
    already_posted instead of double-posting."""
    out = _cycle_dir(args["workdir"], args["pass_id"])
    cycle = json.loads((out / "CYCLE.json").read_text())
    artifacts = {}
    for key, fname in cycle["artifacts"].items():
        artifacts[key] = json.loads((out / fname).read_text())
    wf = args["workflow_id"]

    def payload(stage: str, kind_marker: str, payload_obj: dict) -> dict:
        marker = f"<!-- n5-emit:{wf}:{stage} -->"
        body = (f"{kind_marker}\n{marker}\n"
                f"[MUSEai]@{{role:{{temporal-integration}}}} N5 ledger "
                f"emission — pass `{args['pass_id']}`, stage `{stage}`, "
                f"workflow `{wf}` (idempotency key = workflow ID + stage).\n\n"
                f"```json\n{json.dumps(payload_obj, indent=2)}\n```")
        return {"stage": stage, "marker": marker,
                "sha256": _sha(payload_obj), "body": body}

    jobs = [
        ("ballot_round1", LEDGER_TITLES["generation"],
         "<!-- delphi-generation-ballot v1 -->",
         {"type": "delphi-generation-ballot", "pass_id": args["pass_id"],
          "round": 1, "ballot": artifacts.get("round1")}),
        ("ballot_round2", LEDGER_TITLES["generation"],
         "<!-- delphi-generation-ballot v1 -->",
         {"type": "delphi-generation-ballot", "pass_id": args["pass_id"],
          "round": 2, "ballot": artifacts.get("round2")}),
        ("calibration", LEDGER_TITLES["generation"],
         "<!-- delphi-generation-calibration v1 -->",
         {"type": "delphi-generation-calibration",
          "pass_id": args["pass_id"],
          "calibration": artifacts.get("calibration")}),
        ("calibration_feed_weights", LEDGER_TITLES["weights"],
         "<!-- delphi-generation-calibration v1 -->",
         {"type": "delphi-generation-calibration",
          "pass_id": args["pass_id"],
          "ledger_feed": cycle.get("ledger_feed")}),
    ]
    receipts = []
    for stage, title, kind_marker, obj in jobs:
        if obj.get("ballot") is None and obj.get("calibration") is None \
                and obj.get("ledger_feed") is None:
            receipts.append({"stage": stage, "state": "specified_not_run",
                             "reason": "stage produced no artifact"})
            continue
        p = payload(stage, kind_marker, obj)
        if args["ledger_mode"] == "record_only":
            (out / f"EMIT-{stage}.md").write_text(p["body"])
            receipts.append({"stage": stage, "state": "recorded_only",
                             "sha256": p["sha256"], "marker": p["marker"]})
            continue
        issue = resolve_issue_by_title(title)
        prior = _already_posted(issue, p["marker"])
        if prior:
            receipts.append({"stage": stage, "state": "already_posted",
                             "issue": issue, **prior,
                             "sha256": p["sha256"]})
            continue
        posted = _gh("POST", f"/repos/{REPO}/issues/{issue}/comments",
                     {"body": p["body"]})
        receipts.append({"stage": stage, "state": "posted", "issue": issue,
                         "comment_id": posted["id"],
                         "sha256": p["sha256"]})
    (out / "EMISSION.json").write_text(json.dumps(receipts, indent=2) + "\n")
    return {"workflow_id": wf, "receipts": receipts}


ACTIVITIES = [generate_pass_activity, cross_vote_round1_activity,
              expectations_synthesis_activity,
              run_implementation_suites_activity, equalize_activity,
              finalize_cycle_activity, emit_records_activity]
