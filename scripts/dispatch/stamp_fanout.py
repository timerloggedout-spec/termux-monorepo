#!/usr/bin/env python3
"""Dispatch stamp fan-out — the Swarm routing layer's emission point.

Owner routing update (2026-11-01): every routed+assigned dispatch emits
its full stamp {task class, arm/provider, model, run id, outcome,
quota/cost class} to EACH scoring plane's intake (HindSight/Provenance
substrate), not just the desk-feed. One canonical stamp in, four plane
intakes out:

  1. 3L0        ops/3l0/intake.jsonl                       (3l0-intake/v1, append-only)
  2. DoE        ops/challenge/desk-feed.json               (traversals[].provider_usage[] carrier)
  3. DoE/MVT/ATES experiments/doe/routed-dispatch/records/ (EXPERIMENT schema 1.0 record per dispatch)
  4. MoneyBall  ops/moneyball/dispatch-intake.jsonl        (scoring-feed intake; rows land UNSCORED —
                                                            the plane's method work stays the plane's)

Honesty discipline (binding, per the planes' intake specs): a field the
dispatch does not establish is emitted as null / NOT_ESTABLISHED, never
invented. Usage value is null unless measured/estimated. Emission is
idempotent per dispatch_id.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

NE = "NOT_ESTABLISHED"
CAMPAIGN = "routed-dispatch"
COHORT = "routed-dispatch-2026-11"
MANAGER_POLICY = "swarm-routing/v2 (owner routing update 2026-11-01)"


def _instance_key(root: Path, instance: dict) -> str | None:
    """instance_key per scripts/doe/instance_key.py, when the tuple is complete."""
    try:
        sys.path.insert(0, str(root))
        from scripts.doe.instance_key import instance_key as _ik  # type: ignore
        return _ik(
            provider=instance["provider"],
            model=instance["model"],
            system_prompt_sha256=instance["system_prompt"]["sha256"],
            tools_sha256_=instance["tools"]["sha256"],
            role=instance["role"],
            moniker=instance["moniker"],
            context=instance["context"],
        )
    except Exception:
        return None


def _status_map(status: str) -> str:
    return {"completed": "passed", "failed": "failed"}.get(status, "observed")


def emit(stamp: dict, root: Path, head_sha: str | None = None) -> dict:
    dispatch_id = stamp["dispatch_id"]
    ts = stamp["ts"]
    run = stamp.get("run") or {}
    outcome = stamp.get("outcome") or {}
    quota = stamp.get("quota") or {}
    usage = stamp.get("usage") or {"status": "not_established", "value": None, "unit": None, "source": None}
    if usage.get("status") not in ("measured", "estimated"):
        usage = {**usage, "value": None}
    provider = stamp.get("provider")
    model = stamp.get("model")
    instance = stamp.get("instance")
    run_url = None
    if run.get("run_id"):
        run_url = f"https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/{run['run_id']}"

    # Idempotency: a dispatch_id already in the 3L0 intake is fully emitted.
    intake_path = root / "ops/3l0/intake.jsonl"
    if intake_path.exists():
        for line in intake_path.read_text().splitlines():
            if line.strip() and json.loads(line).get("dispatch_id") == dispatch_id:
                return {"dispatch_id": dispatch_id, "emitted": False, "reason": "already emitted"}

    # ---- 1. 3L0 intake (3l0-intake/v1) ----
    if instance:
        inst_out = {
            "system_prompt": {"ref": instance["system_prompt"]["ref"], "sha256": instance["system_prompt"]["sha256"]},
            "tools": {"ref": instance["tools"]["ref"], "sha256": instance["tools"]["sha256"]},
            "instance_key": _instance_key(root, instance) or NE,
        }
    else:
        inst_out = {"system_prompt": {"ref": NE, "sha256": NE}, "tools": {"ref": NE, "sha256": NE}, "instance_key": NE}
    rec_3l0 = {
        "schema": "3l0-intake/v1",
        "dispatch_id": dispatch_id,
        "ts": ts,
        "provider": provider or NE,
        "model": model or NE,
        "endpoint": stamp.get("endpoint") or (f"{provider}::{model}" if provider and model else NE),
        "moniker": stamp.get("moniker") or NE,
        "role": stamp.get("role") or NE,
        "context": stamp.get("context") or stamp.get("task_class") or NE,
        "instance": inst_out,
        "run": {"session_id": run.get("session_id"), "workflow": run.get("workflow"), "run_id": run.get("run_id")},
        "outcome": {
            "status": outcome.get("status") or NE,
            "gate_call": outcome.get("gate_call"),
            "confirmed": outcome.get("confirmed"),
            "artifact": outcome.get("artifact"),
        },
        "usage": {"tokens_in": usage.get("tokens_in"), "tokens_out": usage.get("tokens_out"),
                  "latency_ms": usage.get("latency_ms"), "retries": usage.get("retries")},
        "quota": {"pool": quota.get("pool"), "slice": quota.get("slice"), "cost_class": quota.get("cost_class")},
        "origin": stamp.get("origin", "live"),
    }
    intake_path.parent.mkdir(parents=True, exist_ok=True)
    with intake_path.open("a") as fh:
        fh.write(json.dumps(rec_3l0, sort_keys=True) + "\n")

    # ---- 2. MoneyBall scoring-feed intake (unscored by design) ----
    mb_path = root / "ops/moneyball/dispatch-intake.jsonl"
    rec_mb = {
        "schema": "moneyball-dispatch-intake/v1",
        "dispatch_id": dispatch_id,
        "ts": ts,
        "task_class": stamp.get("task_class"),
        "provider": provider,
        "model": model,
        "run_id": run.get("run_id"),
        "outcome_status": outcome.get("status"),
        "quota_cost_class": quota.get("cost_class"),
        "evidence_refs": [run_url] if run_url else [],
        "axes": None,
        "score_state": "unscored",
        "origin": stamp.get("origin", "live"),
    }
    mb_path.parent.mkdir(parents=True, exist_ok=True)
    with mb_path.open("a") as fh:
        fh.write(json.dumps(rec_mb, sort_keys=True) + "\n")

    # ---- 3. EXPERIMENT record (DoE scored records + MVT/ATES intake) ----
    baseline = stamp.get("baseline_sha") or head_sha
    candidate = stamp.get("candidate_sha") or head_sha
    if not (baseline and candidate):
        raise SystemExit("baseline/candidate SHA unavailable: pass --head-sha or include SHAs in the stamp")
    exp_instance = None
    if instance:
        exp_instance = {
            "provider": instance["provider"],
            "model": instance["model"],
            "system_prompt": {"ref": instance["system_prompt"]["ref"], "sha256": instance["system_prompt"]["sha256"]},
            "tools": {"ref": instance["tools"]["ref"], "sha256": instance["tools"]["sha256"]},
            "role": instance["role"],
            "moniker": instance["moniker"],
            "context": instance["context"],
            "instance_key": _instance_key(root, instance),
        }
    rec_exp = {
        "schema_version": "1.0",
        "experiment_id": CAMPAIGN,
        "observed_at": ts,
        "baseline_sha": baseline,
        "candidate_sha": candidate,
        "suite": stamp.get("suite") or "routed-dispatch/v1",
        "cohort": COHORT,
        "treatment": {
            "manager_policy_id": MANAGER_POLICY,
            "provider": provider,
            "model": model,
            "arm": provider,
            "instance": exp_instance,
        },
        "status": _status_map(outcome.get("status", "")),
        "outcome": outcome.get("summary"),
        "provenance": "github",
        "confidence": "high",
        "evidence_refs": [run_url] if run_url else [],
        "session_id": run.get("session_id"),
        "window": None,
        "usage": {"status": usage.get("status", "not_established"), "value": usage.get("value"),
                  "unit": usage.get("unit"), "source": usage.get("source")},
        "metrics": {
            "task_class": stamp.get("task_class"),
            "quota_cost_class": quota.get("cost_class"),
            "dispatch_status": outcome.get("status"),
            "set_index": stamp.get("set_index"),
            "cumulative_n": stamp.get("cumulative_n"),
            "selection_reason": stamp.get("selection_reason"),
            "ates_outcome": None,
        },
    }
    rec_dir = root / f"experiments/doe/{CAMPAIGN}/records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in dispatch_id)
    (rec_dir / f"{safe}.json").write_text(json.dumps(rec_exp, indent=2, sort_keys=True) + "\n")

    # ---- 4. DoE live carrier: desk-feed traversal provider_usage ----
    feed_path = root / "ops/challenge/desk-feed.json"
    feed = json.loads(feed_path.read_text())
    trav = next((t for t in feed.get("traversals", []) if t.get("entry") == CAMPAIGN), None)
    if trav is None:
        trav = {"entry": CAMPAIGN, "project": "Routed dispatch stamp carrier (DoE intake, docs/ops/DOE-SCORING-INTAKE.md)",
                "status": "live", "provider_usage": []}
        feed.setdefault("traversals", []).append(trav)
    trav.setdefault("provider_usage", []).append({
        "provider": provider or NE,
        "via": run.get("workflow") or NE,
        "session_id": run.get("session_id"),
        "state": "landed" if outcome.get("status") == "completed" else (outcome.get("status") or NE),
        "usage": {"value": usage.get("value"), "unit": usage.get("unit"), "source": usage.get("source"),
                  "window": None, "match": None,
                  "note": f"dispatch {dispatch_id}: routed stamp fan-out (swarm-routing/v2); consumption per usage.status.",
                  "status": usage.get("status", "not_established")},
        "model": model or NE,
        "phrases": NE,
    })
    feed_path.write_text(json.dumps(feed, indent=2) + "\n")

    return {"dispatch_id": dispatch_id, "emitted": True,
            "targets": ["ops/3l0/intake.jsonl", "ops/moneyball/dispatch-intake.jsonl",
                        f"experiments/doe/{CAMPAIGN}/records/{safe}.json", "ops/challenge/desk-feed.json"]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stamp", required=True, help="Path to the canonical stamp JSON, or - for stdin")
    ap.add_argument("--root", default=".", help="Repo root (default: cwd)")
    ap.add_argument("--head-sha", default=None, help="Fallback baseline/candidate SHA (e.g. github.sha)")
    args = ap.parse_args()
    raw = sys.stdin.read() if args.stamp == "-" else Path(args.stamp).read_text()
    result = emit(json.loads(raw), Path(args.root), head_sha=args.head_sha)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
