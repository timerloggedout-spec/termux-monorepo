#!/usr/bin/env python3
"""Offline triage and opt-in local dual-gate validation; never live authorization."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from dependency_phase_engine import evaluate_plan, load_json, plan_digest  # noqa: E402

GATES = (("repo_gate", "scripts/ci/repo_gate.py"), ("termux_smoke", "scripts/ci/termux_smoke.py"))
TIMEOUT_SECONDS = 240


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()


def lock_path() -> Path:
    common = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir"))
    return common / "flywheel-execute.lock"


def source_provenance() -> dict[str, Any]:
    """Bind HEAD, tracked working/index delta, and actual executable source bytes."""
    paths = [HERE, HERE.parent / "dependency_phase_engine.py"] + [ROOT / p for _, p in GATES]
    delta = git("diff", "--binary") + "\0" + git("diff", "--cached", "--binary")
    return {"repository_head": git("rev-parse", "HEAD"),
            "tracked_diff_sha256": hashlib.sha256(delta.encode()).hexdigest(),
            "executable_sha256": {str(p.relative_to(ROOT)): sha256_file(p) for p in paths}}


def run_gates() -> tuple[str, list[dict[str, Any]]]:
    results = []
    for name, relative in GATES:
        try:
            completed = subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, timeout=TIMEOUT_SECONDS,
                                       check=False, shell=False)
            results.append({"gate": name, "exit_code": completed.returncode,
                            "output_sha256": hashlib.sha256(completed.stdout).hexdigest()})
            if completed.returncode:
                return "FAIL", results
        except subprocess.TimeoutExpired as error:
            output = error.stdout or b""
            if isinstance(output, str):
                output = output.encode()
            results.append({"gate": name, "timeout_seconds": TIMEOUT_SECONDS,
                            "output_sha256": hashlib.sha256(output).hexdigest()})
            return "FAIL", results
        except OSError as error:
            results.append({"gate": name, "error_type": type(error).__name__})
            return "FAIL", results
    return "PASS", results


def make_report(plan: dict[str, Any], snapshot: dict[str, Any], phase_id: str | None,
                execute: bool, *, snapshot_file: Path | None = None,
                plan_file: Path | None = None) -> tuple[dict[str, Any], int]:
    evaluated = evaluate_plan(plan, snapshot)
    triage = sorted(evaluated["evaluations"], key=lambda row: (row["wave"], row["phase_id"]))
    if phase_id is not None and not any(row["phase_id"] == phase_id for row in triage):
        raise ValueError("unknown phase")
    eligible = [row for row in triage if row["state"] == "ready"]
    chosen = phase_id if phase_id is not None else (eligible[0]["phase_id"] if eligible else None)
    selected = next((row for row in triage if row["phase_id"] == chosen), None)
    status, reason = "PASS", "offline evaluation only; no gates executed"
    gates: list[dict[str, Any]] = []
    source = source_provenance()
    if execute:
        status, reason = "BLOCKED", "selected phase is not ready"
        if selected is not None and selected["state"] == "ready":
            with lock_path().open("a") as lock:
                try:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    reason = "another local validation holds the repository lock"
                else:
                    try:
                        # Revalidate after acquiring the lock. Never silently switch evidence.
                        fresh_snapshot = load_json(snapshot_file) if snapshot_file is not None else snapshot
                        fresh_plan = load_json(plan_file) if plan_file is not None else plan
                        latest = evaluate_plan(fresh_plan, fresh_snapshot)
                        current = next((row for row in latest["evaluations"] if row["phase_id"] == chosen), None)
                        if plan_digest(fresh_plan) != plan_digest(plan) or plan_digest(fresh_snapshot) != plan_digest(snapshot):
                            reason = "input evidence changed; reevaluate before execution"
                        elif current is None or current["state"] != "ready":
                            reason = "selected phase is no longer ready"
                        else:
                            source = source_provenance()
                            status, gates = run_gates()
                            reason = "local dual gates passed" if status == "PASS" else "local gate failed or timed out"
                            if source != source_provenance():
                                status, reason = "FAIL", "source changed during validation"
                            if ((snapshot_file is not None and plan_digest(load_json(snapshot_file)) != plan_digest(snapshot))
                                    or (plan_file is not None and plan_digest(load_json(plan_file)) != plan_digest(plan))):
                                status, reason = "FAIL", "input evidence changed during validation"
                    finally:
                        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    receipt = {"schema_version": 1, "mode": "execute" if execute else "report",
               "repository_head": source["repository_head"], "source": source,
               "plan_sha256": plan_digest(plan), "snapshot_sha256": plan_digest(snapshot),
               "selected_phase": chosen, "status": status, "reason": reason,
               "execution_status": status if execute else "NOT_RUN", "task_outcome": "UNKNOWN",
               "deployed": False, "idempotency_key": selected["idempotency_key"] if selected else None,
               "gates": gates, "feedback_posted": False}
    return {"receipt": receipt, "evaluations": evaluated["evaluations"], "triage": triage,
            "handoff": {"phase_id": chosen, "idempotency_key": receipt["idempotency_key"],
                        "eligible": bool(selected and selected["state"] == "ready"), "dispatched": False,
                        "note": "Offline snapshot only; not live authorization."}}, (1 if status in {"BLOCKED", "FAIL"} else 0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--phase")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan, snapshot = load_json(args.plan), load_json(args.snapshot)
        report, code = make_report(plan, snapshot, args.phase, args.execute,
                                   snapshot_file=args.snapshot, plan_file=args.plan)
    except Exception as error:
        # Do not echo input contents, arbitrary paths, or subprocess diagnostics.
        report = {"receipt": {"schema_version": 1, "mode": "execute" if args.execute else "report",
                              "status": "BLOCKED", "execution_status": "BLOCKED" if args.execute else "NOT_RUN",
                              "task_outcome": "UNKNOWN", "deployed": False, "feedback_posted": False},
                  "error_type": type(error).__name__}
        code = 1
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
